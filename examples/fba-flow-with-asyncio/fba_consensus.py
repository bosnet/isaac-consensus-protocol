import enum
import json

from network import (
    BaseTransport,
    Message,
    Node,
    Quorum,
)
from util import (
    log,
    BaseEnum,
)


class Storage:
    messages = None
    message_ids = None

    ballot_history = None

    pending = None
    pending_ids = None

    def __init__(self, node):
        assert isinstance(node, Node)

        self.node = node

        self.messages = list()
        self.message_ids = list()

        self.pending = list()
        self.pending_ids = list()

        self.ballot_history = dict()

    def add(self, ballot):
        assert isinstance(ballot, Ballot)
        assert not ballot.is_empty()
        assert ballot.state == State.all_confirm

        self.messages.append(ballot.message)
        self.message_ids.append(ballot.message.message_id)
        self.ballot_history[ballot.message.message_id] = ballot.to_dict()

        log.storage.info('%s: ballot was added: %s', self.node.name, ballot)

        return

    def is_exists(self, message):
        return message.message_id in self.message_ids

    def add_pending(self, message):
        assert isinstance(message, Message)

        self.pending.append(message)
        self.pending_ids.append(message.message_id)

        log.storage.info('%s: message was added to pending: %s', self.node.name, message)

        return

    def is_exists_pending(self, message):
        return message.message_id in self.pending_ids


class BallotVoteResult(BaseEnum):
    agree = 'Y'
    disagree = 'N'


class State(BaseEnum):
    none = enum.auto()
    init = enum.auto()
    sign = enum.auto()
    accept = enum.auto()
    all_confirm = enum.auto()

    def get_next(self):
        for i in list(self.__class__):
            if i.value > self.value:
                return i

        return None

    def is_next(self, state):
        return state.value > self.value

    def __gt__(self, state):
        return self.value > state.value

    def __lt__(self, state):
        return self.value < state.value

    def __ge__(self, state):
        return self.value >= state.value

    def __le__(self, state):
        return self.value <= state.value

    def __eq__(self, state):
        return self.value == state.value


class Ballot:
    # class AlreadyVotedError(Exception):
    #     pass

    class InvalidBallotError(Exception):
        pass

    class NotExpectedBallotError(Exception):
        pass

    state = None
    name = None
    message = None
    voted = None
    is_broadcasted = None
    node_result = None

    def __init__(self, node, state, node_result):
        assert isinstance(node, Node)
        assert isinstance(node.quorum, Quorum)
        assert isinstance(state, State)

        self.node = node
        self.state = state
        self.state_history = [State.none]
        self.message = None
        self.voted = dict()
        self.vote_history = dict()
        self.is_broadcasted = False
        self.node_result = node_result

    def __repr__(self):
        return '<Ballot: node=%(node)s state=%(state)s voted=%(voted)s node_result=%(node_result)s is_broadcasted=%(is_broadcasted)s>' % self.__dict__  # noqa

    def to_dict(self):
        vh = dict()
        for state, voted in self.vote_history.items():
            copied = dict()
            for node_name, result in voted.items():
                copied[node_name] = result.name

            vh[state] = copied

        return dict(
            node=self.node.to_dict(simple=True),
            state=self.state.name,
            state_history=list(map(lambda x: x.name, self.state_history)),
            node_result=self.node_result.name,
            message=self.message.to_dict(),
            vote_history=vh,
        )

    def is_valid_ballot_message(self, ballot_message):
        # if self.state != ballot_message.state:
        #     return False

        if ballot_message.message is None:
            return False

        if self.message != ballot_message.message:
            return False

        return True

    def initialize_state(self):
        self.state = State.init
        self.message = None
        self.voted = dict()
        self.is_broadcasted = False
        self.node_result = None

        log.ballot.warning('%s: ballot is initialized', self.node.name)

        return

    def change_state(self, state):
        assert isinstance(state, State)

        log.ballot.warning(
            '%s: state changed `%s` -> `%s`',
            self.node.name, self.state.name, state.name,
        )
        self.state_history.append(state)
        if self.state.value in self.voted:
            self.vote_history[self.state.name] = self.voted[self.state.value]

        self.state = state
        self.voted = dict()
        self.is_broadcasted = False

        return

    def serialize_ballot_message(self):
        return BallotMessage(
            self.node,
            self.state,
            self.message,
            self.node_result,
        ).serialize()

    def set_message(self, message):
        assert isinstance(message, Message)

        self.message = message
        self.voted = dict()

        return

    def is_empty(self):
        return self.message is None

    def is_voted(self, node):
        return node.name in self.voted

    def vote(self, node, result, state):
        assert isinstance(node, Node)

        if self.state > state:
            log.ballot.debug(
                '%s: same message and previous state: %s: %s',
                self.node.name,
                state,
            )

            return

        self.voted.setdefault(state.value, dict())

        # if node.name in self.voted:
        #     raise Ballot.AlreadyVotedError('node, %s already voted' % node_name)
        #     return
        if node.name in self.voted[state.value]:
            # existing vote will be overrided
            log.ballot.debug('%s: already voted?: %s', self.node.name)

        self.voted[state.value][node.name] = result
        log.ballot.info('%s: %s voted for %s', self.node.name, node, self.message)

        return

    def check_threshold(self):
        voted = self.voted.copy()

        states = sorted(voted.keys(), reverse=True)
        if len(states) < 1:
            return (self.state, False)

        for state_value in states:
            if state_value < self.state.value:
                del self.voted[state_value]
                continue

            target = voted[state_value]

            agreed_votes = list(filter(lambda x: x == BallotVoteResult.agree, target.values()))

            is_passed = len(agreed_votes) >= self.node.quorum.minimum_quorum
            log.ballot.info(
                '%s: threshold checked: threshold=%s voted=%s minimum_quorum=%s agreed=%d is_passed=%s',  # noqa
                self.node.name,
                self.node.quorum.threshold,
                sorted(map(lambda x: (x[0], x[1].value), target.items())),
                self.node.quorum.minimum_quorum,
                len(agreed_votes),
                is_passed,
            )

            if is_passed:
                return (State.from_value(state_value), is_passed)

        return (self.state, is_passed)


class BallotMessage:
    class InvalidBallotMessageError(Exception):
        pass

    state = None
    message = None
    result = None

    def __init__(self, node, state, message, result):
        assert isinstance(node, Node)
        assert isinstance(state, State)
        assert isinstance(message, Message)
        assert isinstance(result, BallotVoteResult)

        self.node = node
        self.state = state
        self.message = message
        self.result = result

    def __repr__(self):
        return '<BallotMessage: node=%(node)s state=%(state)s result=%(result)s message=%(message)s>' % self.__dict__  # noqa

    def serialize(self):
        return json.dumps(dict(
            type_name='ballot-message',
            node=self.node.name,
            state=self.state.name,
            message=self.message.to_message_dict(),
            result=self.result.name,
        )) + '\r\n\r\n'

    @classmethod
    def from_json(cls, data):
        try:
            o = json.loads(data)
        except json.decoder.JSONDecodeError as e:
            raise cls.InvalidBallotMessageError(e)

        if 'type_name' not in o or o['type_name'] != 'ballot-message':
            raise cls.InvalidBallotMessageError('`type_name` is not "ballot-message"')

        message = None
        try:
            message = Message.from_dict(o)
        except Message.InvalidMessageError as e:
            raise cls.InvalidBallotMessageError(e)

        return cls(
            Node(o['node'], None, None),
            State.from_name(o['state']),
            message,
            BallotVoteResult.from_name(o['result']),
        )

    def get_message(self):
        return self.message


class Consensus:
    name = None
    quorum = None
    ballot = None

    storage = None

    def __init__(self, node, quorum, transport):
        assert isinstance(node, Node)
        assert isinstance(quorum, Quorum)
        assert isinstance(transport, BaseTransport)

        self.node = node
        self.quorum = quorum
        self.transport = transport
        self.storage = Storage(self.node)

        self.ballot = Ballot(self.node, State.none, None)
        self.ballot.change_state(State.init)

        log.consensus.debug(
            '%s: initially set state to %s',
            self.node.name, self.ballot.state,
        )

    def __repr__(self):
        return '<Consensus: node=%(node)s quorum=%(quorum)s transport=%(transport)s>' % self.__dict__  # noqa

    def validate_message(self, message):
        assert isinstance(message, Message)

        # TODO implement
        is_validated = True

        return is_validated

    def receive(self, data):
        log.consensus.debug('%s: received data: %s', self.node.name, data)

        try:
            loaded = load_message(data)
        except Message.InvalidMessageError as e:
            log.consensus.error('unknown data was received: %s', e)
            return
        else:
            log.consensus.debug('%s: received data is %s', self.node.name, loaded)
            if not isinstance(loaded, (Message, BallotMessage)):
                log.consensus.debug('%s: unknown instance found, `%s`', self.node.name, loaded)
                return

        if self.storage.is_exists(loaded.get_message()):
            log.consensus.debug('%s: already stored: %s', self.node.name, loaded)

            return

        if isinstance(loaded, Message):
            return self._handle_message(loaded)

        if isinstance(loaded, BallotMessage):
            return self._handle_ballot_message(loaded)

    def broadcast(self, ballot_message, skip_nodes=None):
        assert type(skip_nodes) in (list, tuple) if skip_nodes is not None else True

        for node in self.quorum.validators:
            if skip_nodes is not None and node in skip_nodes:
                continue

            self.transport.send(
                node.endpoint,
                ballot_message,
            )

        self.ballot.is_broadcasted = True

        return

    def _handle_message(self, message):
        assert message.node is not None

        log.consensus.debug('%s: received message: %s', self.node.name, message)

        if self.ballot.state != State.init:
            log.consensus.debug(
                '%s: ballot state is not `init`, this message will be in stacked in pending storage',  # noqa
                self.node.name,
                message,
            )
            self.storage.add_pending(message.copy())

            return

        if self.ballot.state == State.init:
            if self.ballot.is_empty():
                self.ballot.set_message(message.copy())
            else:
                self.storage.add_pending(message.copy())

                return

        result = BallotVoteResult.disagree
        if self.validate_message(message):
            result = BallotVoteResult.agree

        self.ballot.node_result = result
        self.ballot.vote(self.node, self.ballot.node_result, State.init)

        ballot_message = self.ballot.serialize_ballot_message()
        log.consensus.debug(
            '%s: broadcast ballot_message initially: %s',
            self.node.name,
            ballot_message.strip(),
        )

        self.broadcast(ballot_message, skip_nodes=(message.node,))

        return False

    def _handle_ballot_message(self, ballot_message):
        log.consensus.debug(
            '%s: %s: received ballot_message: %s',
            self.node.name,
            self.ballot.state,
            ballot_message,
        )

        # if ballot_message is from unknown node, just ignore it
        if not self.quorum.is_inside(ballot_message.node):
            log.consensus.debug(
                '%s: message from outside quorum: %s',
                self.node.name,
                ballot_message,
            )
            return

        # if ballot_message.state is older than state of node, just ignore it
        if ballot_message.state < self.ballot.state:
            return

        is_ballot_empty = self.ballot.is_empty()
        log.consensus.debug('%s: ballot is empty?: %s', self.node.name, is_ballot_empty)
        if is_ballot_empty:  # ballot is empty, just embrace ballot
            self.ballot.set_message(ballot_message.message)

        is_valid_ballot_message = self.ballot.is_valid_ballot_message(ballot_message)

        log.consensus.debug(
            '%s: ballot_message is valid?: %s',
            self.node.name,
            is_valid_ballot_message,
        )
        if not is_valid_ballot_message:
            log.consensus.error(
                '%s: unexpected ballot_message was received: expected != given\n%s\n%s',
                self.node.name,
                self.ballot.__dict__,
                ballot_message.__dict__,
            )
            return

        self.ballot.vote(ballot_message.node, ballot_message.result, ballot_message.state)

        state, is_passed_threshold = self.ballot.check_threshold()

        # if new state was already agreed from other validators, the new ballot
        # will be accepted
        if is_passed_threshold and state != self.ballot.state:
            self.ballot.change_state(state)

        log.consensus.debug(
            '%s: is passed threshold?: %s: %s',
            self.node.name,
            is_passed_threshold,
            ballot_message,
        )

        fn = getattr(self, '_handle_%s' % self.ballot.state.name)
        result = fn(ballot_message, is_passed_threshold)

        if result is not True:
            return

        next_state = self.ballot.state.get_next()
        if next_state is None:
            return

        self.ballot.change_state(next_state)

        if next_state == State.all_confirm:
            self._handle_all_confirm(ballot_message, None)
            return

        result = BallotVoteResult.disagree
        if self.validate_message(ballot_message.message):
            result = BallotVoteResult.agree

        self.ballot.node_result = result
        self.ballot.vote(self.node, self.ballot.node_result, self.ballot.state)

        self.broadcast(self.ballot.serialize_ballot_message())

        log.consensus.debug('%s: new ballot broadcasted: %s', self.node.name, self.ballot)

        return

    def _handle_init(self, ballot_message, is_passed_threshold):
        assert isinstance(ballot_message, BallotMessage)

        if self.ballot.node_result is None:
            result = BallotVoteResult.disagree
            if self.validate_message(ballot_message.message):
                result = BallotVoteResult.agree

            self.ballot.node_result = result
            self.ballot.vote(self.node, result, self.ballot.state)

        if not self.ballot.is_broadcasted:
            self.broadcast(self.ballot.serialize_ballot_message())

            log.consensus.debug('%s: new ballot broadcasted: %s', self.node.name, self.ballot)

        if is_passed_threshold:
            return True

        return False

    def _handle_sign(self, ballot_message, is_passed_threshold):
        if is_passed_threshold:
            return True

        return False

    _handle_accept = _handle_sign

    def _handle_all_confirm(self, ballot_message, is_passed_threshold):
        log.consensus.info('%s: %s: %s', self.node.name, self.ballot.state, ballot_message)

        self.storage.add(self.ballot)

        self.ballot.initialize_state()

        # FIXME this is for simulation purpose
        self.reached_all_confirm(ballot_message)

        return

    def reached_all_confirm(self, ballot_message):
        pass


def load_message(data):
    try:
        o = json.loads(data)
    except json.decoder.JSONDecodeError as e:
        raise Message.InvalidMessageError(e)

    if 'type_name' not in o:
        raise Message.InvalidMessageError('field, `type_name` is missing: %s', o)

    if o['type_name'] == 'message':
        return Message.from_json(data)

    if o['type_name'] == 'ballot-message':
        return BallotMessage.from_json(data)
