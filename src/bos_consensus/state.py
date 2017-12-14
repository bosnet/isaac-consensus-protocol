import logging

from .statekind import StateKind
from .ballot import Ballot


log = logging.getLogger(__name__)


class State:
    def __init__(self, node, kind=StateKind.INIT):
        self.node = node
        self.kind = kind

    def handle_ballot(self, ballot):
        assert isinstance(ballot, Ballot)
        self.handle_ballot_impl(ballot)

    def handle_ballot_impl(self, ballot):
        raise NotImplementedError()

    def __eq__(self, state):
        assert isinstance(state, State)
        return self.kind == state.kind


class InitState(State):
    def __init__(self, node):
        super(InitState, self).__init__(node, StateKind.INIT)

    def handle_ballot_impl(self, ballot):
        self.node.node_state = SignState(self.node)

    def __str__(self):
        return 'INIT'


class SignState(State):
    def __init__(self, node):
        super(SignState, self).__init__(node, StateKind.SIGN)

    def handle_ballot_impl(self, ballot):
        if ballot.node_state.kind == self.kind:
            ballots = self.node.validator_ballots
            validator_th = self.node.n_th

            for node_id, node_ballot in ballots.items():
                if node_id == ballot.node_id:
                    continue
                if node_ballot.node_state.kind == self.kind and ballot.message == node_ballot.message:
                    validator_th -= 1

            if validator_th == 0:
                self.node.node_state = AcceptState(self.node)

        self.node.store(ballot)

    def __str__(self):
        return 'SIGN'


class AcceptState(State):
    def __init__(self, node):
        super(AcceptState, self).__init__(node, StateKind.ACCEPT)

    def handle_ballot_impl(self, ballot):
        if ballot.node_state.kind == self.kind:
            ballots = self.node.validator_ballots
            validator_th = self.node.n_th
            for node_id, node_ballot in ballots.items():
                if node_id == ballot.node_id:
                    continue
                if node_ballot.node_state.kind == self.kind and ballot.message == node_ballot.message:
                    validator_th -= 1

            if validator_th == 0:
                self.node.node_state = AllConfirmState(self.node)

        self.node.store(ballot)

    def __str__(self):
        return 'ACCEPT'


class AllConfirmState(State):
    def __init__(self, node):
        super(AllConfirmState, self).__init__(node, StateKind.ALLCONFIRM)

    def handle_ballot_impl(self, ballot):
        pass

    def __str__(self):
        return 'ALL_CONFIRM'
