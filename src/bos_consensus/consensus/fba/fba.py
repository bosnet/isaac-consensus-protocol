import enum
import math

from bos_consensus.common import Ballot, BallotVotingResult, Node, Slot

from bos_consensus.consensus.base import BaseConsensus
from bos_consensus.middlewares import (
    load_middlewares,
    NoFurtherConsensusMiddlewares,
    StopBroadcast,
    StopStore,
)


class FbaState(enum.IntEnum):
    pass


class Fba(BaseConsensus):

    threshold = None
    validator_candidates = None
    transport = None
    middlewares = list()
    voting_histories = None  # for auditing received ballots
    slot = None

    def __init__(self, node, threshold, validator_candidates):
        assert isinstance(node, Node)
        super(Fba, self).__init__(node)
        assert type(threshold) in (float, int)
        assert threshold <= 100 and threshold > 0  # threshold must be percentile
        assert isinstance(validator_candidates, (list, tuple))
        assert len(
            list(filter(lambda x: not isinstance(x, Node), validator_candidates))
        ) < 1
        self.threshold = threshold
        self.validator_candidates = validator_candidates
        self.__minimum = math.ceil((len(self.validator_candidates) + 1) * (self.threshold / 100))
        self.validator_node_names = tuple([node.name] + list(map(lambda x: x.name, self.validator_candidates)))
        self.validator_connected = dict()
        self.validator_faulty = set()
        self.voting_histories = list()
        self.slot_size = 5
        self.slot = Slot(self.slot_size)
        self.middlewares = load_middlewares('consensus')
        self.set_self_node_to_validators()
        self.init()

    def set_self_node_to_validators(self):
        self.log.debug('[%s] set self node to validators', self.node.name)
        if self.node.name not in self.validator_connected:
            self.add_to_validator_connected(self.node)

        return

    def init(self):
        self.slot.set_all_state(self.get_init_state())
        self.clear_validator_ballots()

        return

    def get_ballot(self, ballot):
        return self.slot.slot[self.slot.get_ballot_index(ballot)]

    def get_init_state(self):
        raise NotImplementedError()

    def get_last_state(self):
        raise NotImplementedError()

    def __repr__(self):
        repr_str = list()
        repr_str.append('threshold=%(threshold)s')
        repr_str.append('candidates=%(validator_candidates)s')
        repr_str.append('connected=%(validator_connected)s')
        repr_str.append('faulty=%(validator_faulty)s')
        return ' '.join(repr_str) % self.__dict__

    def set_state(self, ballot, state):
        if self.slot.get_ballot_state(ballot) == state:
            return

        self.log.metric(
            action='change-state',
            node=self.node.name,
            state=dict(
                after=state.name,
                before=self.get_ballot(ballot).consensus_state.name if self.get_ballot(ballot).consensus_state is not None else None,
            ),
            validators=tuple(self.validator_connected.keys()),
        )

        self.slot.set_ballot_consensus_state(ballot, state)

        return

    def add_to_validator_connected(self, node):
        is_new = node.name not in self.validator_connected
        if is_new:
            self.validator_connected[node.name] = node
            self.log.debug('added to validators: is_new=%s node=%s', is_new, node)
            self.log.metric(action='connected', target=node.name, validators=list(self.validator_connected.keys()))

        return

    def remove_from_validators(self, node):
        if node.name not in self.validator_connected:
            return

        del self.validator_connected[node.name]

        self.log.debug('removed from validators: %s', node)
        self.log.metric(action='removed', target=node.name, validators=list(self.validator_connected.keys()))

        return

    def from_outside(self, name):
        return name not in self.validator_node_names

    def clear_validator_ballots(self):
        self.slot.clear_all_validator_ballots()
        return

    @property
    def minimum(self):
        '''
        the required minimum quorum will be round *up*
        '''
        return self.__minimum

    def to_dict(self, simple=True):
        return dict(
            validator_candidates=list(map(lambda x: x.to_dict(), self.validator_candidates)),
            threshold=self.threshold,
            messages=list(map(lambda x: x.serialize(), self.messages)),
        )

    def all_validators_connected(self):
        return len(self.validator_candidates) + 1 == len(self.validator_connected)

    def handle_ballot(self, ballot):
        '''
        Middleware for broadcast
            1. each middleware execute before and after broadcast
            1. if method of middleware returns,
                * `None`: pass
                * `NoFurtherConsensusMiddlewares`: stop middlewares
                * `StopBroadcast`: stop broadcast
            1. middleware keep the state in `broadcast`
        '''
        assert isinstance(ballot, Ballot)

        middlewares = list(map(lambda x: x(self), self.middlewares))

        for m in middlewares:
            try:
                m.handle_ballot(ballot)
            except NoFurtherConsensusMiddlewares as e:
                self.log.debug('break middleware: %s', e)
                break
            except StopBroadcast as e:
                self.log.debug('stop consensus: %s', e)
                return

        self.log.debug(
            '[%s] [%s] begin handle_ballot=%s',
            self.node.name,
            self.get_ballot(ballot).consensus_state if self.slot.get_ballot_index(ballot) != 'Not Found' else 'None',
            ballot,
        )

        self._handle_ballot(ballot)
        return

    def _handle_ballot(self, ballot):
        raise NotImplementedError()

    def _is_new_ballot(self, ballot):  # [TODO] search in ballot_history
        if self.slot.get_ballot_index(ballot) == 'Not Found' and ballot.message.message_id not in self.message_ids:
            return True
        if not self.get_ballot(ballot).validator_ballots:
            return True
        if self.node.name not in self.get_ballot(ballot).validator_ballots:
            return True
        if ballot.ballot_id != self.get_ballot(ballot).validator_ballots[self.node.name].ballot_id:
            return True
        return False

    def make_self_ballot(self, ballot):
        if self.slot.get_ballot_index(ballot) == 'Not Found':
            self_ballot = Ballot(ballot.ballot_id, self.node.name, ballot.message, self.slot.init_state, BallotVotingResult.agree)
            self_ballot.timestamp = ballot.timestamp
            return self_ballot
        self_ballot = Ballot(ballot.ballot_id, self.node.name, ballot.message, self.slot.get_ballot_state(ballot), BallotVotingResult.agree)
        self_ballot.timestamp = self.get_ballot(ballot).ballot.timestamp
        return self_ballot

    def broadcast(self, ballot, retries=1):
        '''
        Middleware for broadcast
            1. each middleware execute before and after broadcast
            1. if method of middleware returns,
                * `None`: pass
                * `NoFurtherConsensusMiddlewares`: stop middlewares
                * `StopBroadcast`: stop broadcast
            1. middleware keep the state in `broadcast`
        '''
        assert isinstance(ballot, Ballot)

        middlewares = list(map(lambda x: x(self), self.middlewares))

        for m in middlewares:
            try:
                m.broadcast(ballot)
            except NoFurtherConsensusMiddlewares as e:
                self.log.debug('break middleware: %s', e)
                break
            except StopBroadcast as e:
                self.log.debug('stop consensus: %s', e)
                return

        self.log.debug(
            '[%s] [%s] begin broadcast to connected nodes=%s with retries=%d',
            self.node.name,
            self.slot.get_ballot_state(ballot) if ((self.slot.get_ballot_index(ballot)) != 'Not Found') else 'None',
            tuple(self.validator_connected.keys()),
            retries,
        )

        self.store(ballot)
        for node_name, node in self.validator_connected.items():
            if node_name is not self.node.name:
                self.transport.send(node.endpoint, ballot.serialize(to_string=False), retries)

        return

    def store(self, ballot):
        '''
        Middleware for store
            1. each middleware execute before and after store
            1. if method of middleware returns,
                * `None`: pass
                * `NoFurtherConsensusMiddlewares`: stop middlewares
                * `StopStore`: stop store
            1. middleware keep the state in `store`
        '''
        assert isinstance(ballot, Ballot)

        middlewares = list(map(lambda x: x(self), self.middlewares))

        for m in middlewares:
            try:
                m.store(ballot)
            except NoFurtherConsensusMiddlewares as e:
                self.log.debug('break middleware: %s', e)
                break
            except StopStore as e:
                self.log.debug('stop consensus: %s', e)
                return

        if self.slot.get_ballot_index(ballot) != 'Not Found':
            if self.slot.get_ballot_state(ballot) > ballot.state:
                self.log.debug('found state regression ballot=%s state=%s', ballot, self.slot.get_ballot_state(ballot))
                return

        ballot.timestamp = self.get_ballot(ballot).ballot.timestamp

        self.slot.get_validator_ballots(ballot)[ballot.node_name] = ballot
        self.log.debug('ballot stored state=%s ballot=%s', self.slot.get_ballot_state(ballot), ballot)
        return

    def set_faulty_validator(self, node_name):
        if node_name not in self.validator_connected:
            return

        self.validator_faulty.add(node_name)

        self.log.metric(
            action='faulty-node-added',
            faulty_node=node_name,
        )
        return

    def is_guarantee_liveness(self):
        not_connected_yet = len(self.validator_connected) <= 1
        if not_connected_yet:
            return True
        non_faulty_validators = set(self.validator_connected.keys()) - self.validator_faulty
        return len(non_faulty_validators) >= self.minimum
