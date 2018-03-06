import enum
import math

from ...common import Ballot, BallotVotingResult, Node
from ...consensus.base import BaseConsensus
from bos_consensus.middlewares import (
    load_middlewares,
    NoFurtherConsensusMiddlewares,
    StopBroadcast,
    StopStore,
)


class FbaState(enum.IntEnum):
    pass


class Fba(BaseConsensus):
    state = None
    threshold = None
    validator_ballots = None
    validator_candidates = None
    transport = None
    middlewares = list()
    voting_histories = None  # for auditing received ballots

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

        self.validator_ballots = dict()
        self.voting_histories = list()

        self.middlewares = load_middlewares('consensus')
        self.set_self_node_to_validators()

        self.init()

    def set_self_node_to_validators(self):
        self.log.debug('[%s] set self node to validators', self.node.name)
        if self.node.name not in self.validator_connected:
            self.add_to_validator_connected(self.node)

        return

    def init(self):
        self.set_state(self.get_init_state())
        self.clear_validator_ballots()

        return

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

    def set_state(self, state):
        self.log.metric(
            action='change-state',
            node=self.node.name,
            state=dict(
                after=state.name,
                before=self.state.name if self.state is not None else None,
            ),
            validators=tuple(self.validator_connected.keys()),
        )

        self.state = state

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
        self.validator_ballots.clear()

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
        raise NotImplementedError()

    def _is_new_ballot(self, ballot):  # [TODO] search in ballot_history
        if not self.validator_ballots:
            return True
        if ballot.node_name not in self.validator_ballots:
            return True
        if ballot.ballot_id != self.validator_ballots[ballot.node_name].ballot_id:
            return True
        return False

    def make_self_ballot(self, ballot):
        return Ballot(ballot.ballot_id, self.node.name, ballot.message, self.state, BallotVotingResult.agree)

    def broadcast(self, ballot):
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
            '[%s] [%s] begin broadcast to connected nodes=%s',
            self.node.name,
            self.state,
            tuple(self.validator_connected.keys()),
        )

        self.store(ballot)
        for node_name, node in self.validator_connected.items():
            if node_name is not self.node.name:
                self.transport.send(node.endpoint, ballot.serialize(to_string=False))

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

        if self.state > ballot.state:
            self.log.debug('found state regression ballot=%s state=%s', ballot, self.state)

            return

        self.validator_ballots[ballot.node_name] = ballot

        self.log.debug('ballot stored state=%s ballot=%s', self.state, ballot)

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
