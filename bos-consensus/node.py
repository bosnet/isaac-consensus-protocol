import logging
from state import State
from state import InitState
from state import SignState
from state import AcceptState
from state import AllConfirmState
from ballot import Ballot

log = logging.getLogger(__name__)


class Node:
    node_id = None
    address = None
    threshold = None
    validators = None
    validator_ballots = {}

    node_state = None

    state_init = None
    state_sign = None
    state_accept = None
    state_all_confirm = None

    def __init__(self, node_id, address, threshold, validators):
        assert type(address) in (list, tuple) and len(address) == 2
        assert type(address[0]) in (str,) and type(address[1]) in (int,)

        self.node_id = node_id
        self.address = address
        self.validators = validators
        self.threshold = threshold

        self.state_init = InitState(self)
        self.state_sign = SignState(self)
        self.state_accept = AcceptState(self)
        self.state_all_confirm = AllConfirmState(self)

        self.node_state = self.state_init

    def __repr__(self):
        return '<Node: %s(%s)>' % (self.node_id, self.endpoint)

    def __str__(self):
        return '<Node[%s]: %s(%s)>' % (self.node_state.__str__(), self.node_id, self.endpoint)

    @property
    def endpoint(self):
        return 'http://%s:%s' % self.address

    def to_dict(self):
        return dict(
            node_id=self.node_id,
            endpoint=self.endpoint,
            validators=self.validators,
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

    def receive(self, ballot):
        assert isinstance(ballot, Ballot)
        self.node_state.handle_ballot(ballot)

    def get_validator_ballots(self):
        return self.validator_ballots

    def store(self, ballot):
        assert isinstance(ballot, Ballot)
        self.validator_ballots[ballot.node_id] = ballot
        return

    def get_validator_th(self):
        return len(self.validators) * self.threshold // 100
