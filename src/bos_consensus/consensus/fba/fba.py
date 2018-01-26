import copy
import enum
import math


from ...common.ballot import Ballot
from ...consensus.base import BaseConsensus
from ...common.node import Node


class FbaState(enum.IntEnum):
    pass


class Fba(BaseConsensus):
    state = None
    threshold = None
    validators = None
    validator_endpoints = None

    def __init__(self, node, threshold, validator_endpoints):
        assert isinstance(node, Node)
        super(Fba, self).__init__(node)
        assert type(threshold) in (float, int)
        assert threshold <= 100 and threshold > 0  # threshold must be percentile
        assert isinstance(validator_endpoints, list)
        assert len(
            list(filter(lambda x: not isinstance(x, str), validator_endpoints))
        ) < 1

        self.threshold = threshold
        self.validator_endpoints = validator_endpoints
        self.validators = dict()
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

    def __repr__(self):
        return '<Quorum: threshold=%(threshold)s validators=%(validators)s>' % self.__dict__

    def set_state(self, state):
        self.state = state
        self.log.info('[%s] state to %s', self.node_name, self.state)
        return

    def add_to_validators(self, node):
        self.validators[node.name] = {'endpoint': node.endpoint, 'ballot': None}

    def from_outside(self, name):
        return name not in self.validator_node_names()

    def validator_node_names(self):
        return self.validators.keys()

    def clear_validator_ballots(self):
        for key in self.validators.keys():
            if 'ballot' in self.validators[key]:
                self.validators[key]['ballot'] = None

    @property
    def minimum(self):
        '''
        the required minimum quorum will be round *up*
        '''
        return math.ceil((len(self.validator_endpoints) + 1) * (self.threshold / 100))

    def to_dict(self, simple=True):
        return dict(
            validator_endpoints=self.validator_endpoints,
            threshold=self.threshold,
        )

    def all_validators_connected(self):
        return len(self.validator_endpoints) + 1 == len(self.validators)

    def handle_ballot(self, ballot):
        raise NotImplementedError()

    def broadcast(self, ballot):
        assert isinstance(ballot, Ballot)

        self.log.debug('[%s] [%s] begin broadcast to everyone', self.node_name, self.state)

        new = Ballot(ballot.ballot_id, self.node_name, ballot.message, self.state)
        self.store(new)

        for name, node in self.validators.items():
            if name is not self.node_name:
                self.transport.send(node['endpoint'], new.serialize(to_string=False))

        return

    def store(self, ballot):
        assert isinstance(ballot, Ballot)
        if self.state <= ballot.state:
            self.validators[ballot.node_name]['ballot'] = ballot
            self.log.debug('[%s] [%s] store ballot [%s]', self.node_name, self.state, ballot.serialize(to_string=True))

        return
