import enum
import math

from ...common.ballot import Ballot, BallotVotingResult
from ...consensus.base import BaseConsensus
from bos_consensus.middlewares import (
    load_middlewares,
    NoFurtherConsensusMiddlewares,
    StopBroadcast,
    StopStore,
)
from ...common.node import Node


class FbaState(enum.IntEnum):
    pass


class Fba(BaseConsensus):
    state = None
    threshold = None
    validators = None
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
        self.validator_node_names = tuple([node.name] + list(map(lambda x: x.name, self.validator_candidates)))
        self.validators = dict()
        self.middlewares = load_middlewares('consensus')
        self.voting_histories = list()
        self.init()

    def set_self_node_to_validators(self):
        if self.node_name not in self.validators:
            self.add_to_validators(self.node)

        return

    def init(self):
        self.set_state(self.get_init_state())
        self.clear_validator_ballots()

        self.set_self_node_to_validators()

        return

    def get_init_state(self):
        raise NotImplementedError()

    def get_last_state(self):
        raise NotImplementedError()

    def __repr__(self):
        return '<Quorum: threshold=%(threshold)s validators=%(validators)s>' % self.__dict__

    def set_state(self, state):
        self.state = state
        self.log.info('[%s] state to %s', self.node_name, self.state)

        return

    def add_to_validators(self, node):
        is_new = node.name not in self.validators

        self.validators[node.name] = {'node': node, 'ballot': None}

        if is_new:
            self.log.debug('added to validators: is_new=%s node=%s', is_new, node)
            self.log.metric(action='connected', target=node.name, validators=list(self.validators.keys()))

        return

    def remove_from_validators(self, node):
        if node.name not in self.validators:
            return

        del self.validators[node.name]

        self.log.debug('removed from validators: %s', node)
        self.log.metric(action='removed', target=node.name, validators=list(self.validators.keys()))

        return

    def from_outside(self, name):
        return name not in self.validator_node_names

    def clear_validator_ballots(self):
        for key in self.validators.keys():
            if 'ballot' in self.validators[key]:
                self.validators[key]['ballot'] = None

    @property
    def minimum(self):
        '''
        the required minimum quorum will be round *up*
        '''
        return math.ceil((len(self.validator_candidates) + 1) * (self.threshold / 100))

    def to_dict(self, simple=True):
        return dict(
            validator_candidates=list(map(lambda x: x.to_dict(), self.validator_candidates)),
            threshold=self.threshold,
            messages=list(map(lambda x: x.serialize(), self.messages)),
        )

    def all_validators_connected(self):
        return len(self.validator_candidates) + 1 == len(self.validators)

    def handle_ballot(self, ballot):
        raise NotImplementedError()

    def _is_new_ballot(self, ballot):
        if self.node_name not in self.validators or not self.validators[self.node_name]:
            return True
        old_ballot = self.validators[self.node_name]['ballot']
        return not old_ballot or old_ballot.message.data != ballot.message.data  # noqa

    def make_self_ballot(self, ballot):
        return Ballot(ballot.ballot_id, self.node_name, ballot.message, self.state, BallotVotingResult.agree)

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


        self.log.debug('[%s] [%s] begin broadcast to everyone', self.node_name, self.state)

        self.store(ballot)
        for name, validator in self.validators.items():
            if name is not self.node_name:
                self.transport.send(validator['node'].endpoint, ballot.serialize(to_string=False))

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

        self.validators[ballot.node_name]['ballot'] = ballot

        self.log.debug('ballot stored state=%s ballot=%s', self.state, ballot)

        return
