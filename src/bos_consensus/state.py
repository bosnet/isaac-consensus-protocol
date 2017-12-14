import logging

from .statekind import StateKind
from .ballot import Ballot


log = logging.getLogger(__name__)


class State:
    def __init__(self, node, kind=StateKind.NONE):
        self.node = node
        self.kind = kind

    def handle_ballot(self, ballot):
        assert isinstance(ballot, Ballot)
        self.handle_ballot_impl(ballot)

    def init_node(self):
        raise NotImplementedError()

    def handle_ballot_impl(self, ballot):
        raise NotImplementedError()

    def __eq__(self, state):
        assert isinstance(state, State)
        return self.kind == state.kind

    def __str__(self):
        return self.kind.name


class NoneState(State):
    def __init__(self, node):
        super(NoneState, self).__init__(node, StateKind.NONE)

    def init_node(self):
        self.node.set_state_init()

    def handle_ballot_impl(self, ballot):
        pass


class InitState(State):
    def __init__(self, node):
        super(InitState, self).__init__(node, StateKind.INIT)

    def init_node(self):
        pass

    def handle_ballot_impl(self, ballot):
        self.node.set_state_sign()
        self.node.broadcast(ballot.message)


class SignState(State):
    def __init__(self, node):
        super(SignState, self).__init__(node, StateKind.SIGN)

    def init_node(self):
        pass

    def handle_ballot_impl(self, ballot):
        if ballot.node_state_kind == self.kind:
            ballots = self.node.validator_ballots
            validator_th = self.node.n_th

            for node_id, node_ballot in ballots.items():
                if node_id == ballot.node_id:
                    continue
                if node_ballot.node_state_kind == self.kind and ballot.message == node_ballot.message:
                    validator_th -= 1

            if validator_th == 0:
                self.node.set_state_accept()
                self.node.broadcast(ballot.message)

        self.node.store(ballot)


class AcceptState(State):
    def __init__(self, node):
        super(AcceptState, self).__init__(node, StateKind.ACCEPT)

    def init_node(self):
        pass

    def handle_ballot_impl(self, ballot):
        if ballot.node_state_kind == self.kind:
            ballots = self.node.validator_ballots
            validator_th = self.node.n_th
            for node_id, node_ballot in ballots.items():
                if node_id == ballot.node_id:
                    continue
                if node_ballot.node_state_kind == self.kind and ballot.message == node_ballot.message:
                    validator_th -= 1

            if validator_th == 0:
                self.node.set_state_all_confirm()

        self.node.store(ballot)


class AllConfirmState(State):
    def __init__(self, node):
        super(AllConfirmState, self).__init__(node, StateKind.ALLCONFIRM)

    def init_node(self):
        pass

    def handle_ballot_impl(self, ballot):
        pass
