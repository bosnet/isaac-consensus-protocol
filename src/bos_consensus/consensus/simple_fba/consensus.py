import enum
import logging

from ..base import BaseConsensus
from ...ballot import Ballot


log = logging.getLogger(__name__)


class StateKind(enum.IntEnum):
    NONE = enum.auto()
    INIT = enum.auto()
    SIGN = enum.auto()
    ACCEPT = enum.auto()
    ALLCONFIRM = enum.auto()


class BaseState:
    kind = None

    def __new__(cls, *a, **kw):
        assert isinstance(cls.kind, StateKind)

        return super(BaseState, cls).__new__(cls)

    def __init__(self, consensus, node):
        self.consensus = consensus
        self.node = node

    def handle_ballot(self, ballot):
        assert isinstance(ballot, Ballot)
        self.handle_ballot_impl(ballot)

    def init_node(self):
        raise NotImplementedError()

    def handle_ballot_impl(self, ballot):
        raise NotImplementedError()

    def __eq__(self, state):
        assert isinstance(state, BaseState)
        return self.kind == state.kind

    def __str__(self):
        return self.kind.name


class NoneState(BaseState):
    kind = StateKind.NONE

    def init_node(self):
        self.consensus.set_init()

    def handle_ballot_impl(self, ballot):
        pass


class InitState(BaseState):
    kind = StateKind.INIT

    def init_node(self):
        pass

    def handle_ballot_impl(self, ballot):
        self.node.broadcast(ballot.message)
        self.node.store(ballot)
        ballots = self.node.validator_ballots
        validator_th = self.node.minimum_number_of_agreement

        for _, node_ballot in ballots.items():
            if self.kind <= node_ballot.node_state_kind:
                validator_th -= 1

        if validator_th == 0:
            self.consensus.set_sign()
            self.node.broadcast(ballot.message)


class SignState(BaseState):
    kind = StateKind.SIGN

    def init_node(self):
        pass

    def handle_ballot_impl(self, ballot):
        self.node.store(ballot)
        ballots = self.node.validator_ballots
        validator_th = self.node.minimum_number_of_agreement

        for _, node_ballot in ballots.items():
            if self.kind <= node_ballot.node_state_kind:
                validator_th -= 1

        if validator_th == 0:
            self.consensus.set_accept()
            self.node.broadcast(ballot.message)


class AcceptState(BaseState):
    kind = StateKind.ACCEPT

    def init_node(self):
        pass

    def handle_ballot_impl(self, ballot):
        self.node.store(ballot)
        ballots = self.node.validator_ballots
        validator_th = self.node.minimum_number_of_agreement

        for _, node_ballot in ballots.items():
            if self.kind <= node_ballot.node_state_kind:
                validator_th -= 1

        if validator_th == 0:
            self.consensus.set_all_confirm()
            self.node.broadcast(ballot.message)


class AllConfirmState(BaseState):
    kind = StateKind.ALLCONFIRM

    def init_node(self):
        pass

    def handle_ballot_impl(self, ballot):
        # 다른 메시지가 들어오면 INIT 으로 변경
        if (not self.node.messages) or (self.node.messages[-1] != ballot.message):
            self.consensus.set_init()
            ballot.node_state_kind = StateKind.INIT
            self.node.receive_ballot(ballot)

        # 같은 메시지가 들어오면 pass
        else:
            pass
        return


class Consensus(BaseConsensus):
    def initialize(self):
        super(Consensus, self).initialize()

        self.state_none = NoneState(self, self.node)
        self.state_init = InitState(self, self.node)
        self.state_sign = SignState(self, self.node)
        self.state_accept = AcceptState(self, self.node)
        self.state_all_confirm = AllConfirmState(self, self.node)

        self.node_state = self.state_none

    def set_init(self):
        log.info('[%s] state to INIT', self.node.node_id)
        self.node_state = self.state_init

        return

    def set_sign(self):
        log.info('[%s] state to SIGN', self.node.node_id)
        self.node_state = self.state_sign

        return

    def set_accept(self):
        log.info('[%s] state to ACCEPT', self.node.node_id)
        self.node_state = self.state_accept

        return

    def set_all_confirm(self):
        log.info('[%s] state to ALLCONFIRM', self.node.node_id)
        self.node_state = self.state_all_confirm
        self.node.save_message(self.node.validator_ballots[self.node.node_id].message)

        return
