import enum
from urllib.parse import (
    urlparse,
    parse_qs,
)

from .ballot import Ballot
from .consensus import BaseConsensus
from .message import Message
from .network import BaseTransport
from .util import LoggingMixin


def get_node_id_from_addr(a):
    query = urlparse(a).query
    if len(query) < 1:
        return a

    parsed = parse_qs(query)
    if len(parsed) < 1 or 'name' not in parsed or len(parsed['name']) < 1:
        return a

    return parsed['name'][0]


class FaultyNodeKind(enum.Enum):
    # failed to connect to the node or failed to get the proper response from
    # the node.
    NodeUnreachable = enum.auto()

    # in single phase of consensus, the node does not send voting messages.
    NoVoting = enum.auto()

    # the node sends the duplicated, but same messages.
    DuplicatedMessageSent = enum.auto()

    # in single phase of consensus, the node sends different voting with the
    # other nodes on the same message.
    DivergentVoting = enum.auto()

    # the node broadcasts some state of ballot, but he sends again with the
    # previous state of ballot.
    StateRegression = enum.auto()


class Node(LoggingMixin):
    node_id = None
    transport = None
    messages = None
    message_ids = None

    def __init__(self, node_id, address, threshold, validator_addrs, consensus):
        assert type(address) in (list, tuple) and len(address) == 2
        assert type(address[0]) in (str,) and type(address[1]) in (int,)
        assert isinstance(consensus, BaseConsensus)

        super(Node, self).__init__()

        self.node_id = node_id

        self.set_logging('node', node=self.node_id)

        self.address = address
        self.validators = dict((key, False) for key in validator_addrs)
        self.threshold = threshold
        self.minimum_number_of_agreement = (1 + len(self.validators)) * self.threshold // 100
        self.validator_ballots = {}
        self.messages = list()
        self.message_ids = list()

        self.consensus = consensus
        self.consensus.set_node(self)
        self.consensus.initialize()

        self.validator_ids = list(map(get_node_id_from_addr, self.validators))

    def __repr__(self):
        return '<Node: %s(%s)>' % (self.node_id, self.endpoint)

    def __str__(self):
        return '<Node[%s]: %s(%s)>' % (
            self.consensus.node_state.__str__(),
            self.node_id,
            self.endpoint,
        )

    def set_transport(self, transport):
        assert isinstance(transport, BaseTransport)

        self.transport = transport

        return

    @property
    def endpoint(self):
        return 'http://%s:%s?name=%s' % (self.address[0], self.address[1], self.node_id)

    def to_dict(self):
        return dict(
            status=self.consensus.node_state.kind.name,
            node_id=self.node_id,
            threshold=self.threshold,
            address=self.address,
            endpoint=self.endpoint,
            validator_addrs=self.validators,
            messages=self.message_ids,
        )

    def __eq__(self, rhs):
        rhs_endpoint = rhs.endpoint
        lhs_endpoint = self.endpoint

        t_str = '//localhost:'  # target_string
        r_str = '//127.0.0.1:'  # replace_string
        if t_str in rhs_endpoint:
            rhs_endpoint.replace(t_str, r_str)

        if t_str in lhs_endpoint:
            lhs_endpoint.replace(t_str, r_str)
        return lhs_endpoint == rhs_endpoint

    def init_node(self):
        self.consensus.node_state.init_node()
        return

    def clear_validator_ballots(self):
        self.validator_ballots.clear()

    def receive_message_from_client(self, message):
        assert isinstance(message, Message)

        if message.message_id in self.message_ids:
            self.log.debug('message already stored: %s', message)
            return

        ballot = Ballot.new(self.node_id, message, self.consensus.node_state.kind)
        self.consensus.node_state.handle_ballot(ballot)

        self.broadcast(ballot)
        return

    def broadcast(self, ballot):
        assert isinstance(ballot, Ballot)

        ballot.node_state_kind = self.consensus.node_state.kind

        self.log.debug('[%s] [%s] begin broadcast to everyone', self.node_id, self.consensus.node_state)
        for addr in self.validators.keys():
            self.transport.send(addr, ballot.serialize(self.node_id, to_string=False))

        return

    def receive_ballot(self, ballot):
        assert isinstance(ballot, Ballot)

        if ballot.message.message_id in self.message_ids:
            self.log.debug('message already stored: %s', ballot.message)
            return

        from_outside = ballot.node_id not in self.validator_ids
        self.log.debug(
            '[%s] [%s] receive ballot from %s%s',
            self.node_id,
            self.consensus.node_state,
            ballot.node_id,
            '(outside: %s)' % self.validator_ids if from_outside else '',
        )

        self.consensus.node_state.handle_ballot(ballot)

    def store(self, ballot, node_id=None):
        assert isinstance(ballot, Ballot)

        # [TODO] when receive different message?
        if self.consensus.node_state.kind <= ballot.node_state_kind:
            if node_id is not None:
                node_id = node_id
            else:
                node_id = ballot.node_id

            self.validator_ballots[node_id] = ballot

        return

    def save_message(self, message):
        self.messages.append(message)
        self.message_ids.append(message.message_id)

    def all_validators_connected(self):
        for _, connected in self.validators.items():
            if not connected:
                return False

        return True


class Illnode(Node):

    def __init__(self, node_id, address, threshold, validator_addrs, consensus, bad_behavior_percent):
        Node.__init__(self, node_id, address, threshold, validator_addrs, consensus)
        self.bad_behavior_percent = bad_behavior_percent

    def is_bad_behavior(self, bad_behavior_percent):
        from random import randint
        return bad_behavior_percent >= randint(1, 100)

    def receive_ballot(self, ballot):
        if not self.is_bad_behavior(self.bad_behavior_percent):
            Node.receive_ballot(self, ballot)
        else:
            self.log.debug('[%s] is not receiving the ballot from %s' % (self.node_id, ballot.node_id))
