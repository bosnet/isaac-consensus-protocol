import enum

from bos_consensus.consensus.fba import FbaState, Fba
from bos_consensus.common.ballot import Ballot


class IsaacState(FbaState):
    NONE = enum.auto()
    INIT = enum.auto()
    SIGN = enum.auto()
    ACCEPT = enum.auto()
    ALLCONFIRM = enum.auto()

    @classmethod
    def get_from_value(cls, v):
        for i in list(cls):
            if i.value == v:
                return i

        return


class IsaacConsensus(Fba):
    def get_init_state(self):
        return IsaacState.INIT

    def get_last_state(self):
        return IsaacState.ALLCONFIRM

    def handle_ballot(self, ballot):
        # filtering rules, for same `ballot_id` or `message_id`
        #  1. if `message_id` is already saved in `self.message_ids`, it will be passed
        #  1. if `ballot` is same,
        #       - same message
        #       - state
        #   it will be passed.
        #  1. if `ballot` is same except `ballot_id`, it will be passed
        assert isinstance(ballot, Ballot)
        if ballot.node_name in self.validator_ballots:
            existing = self.validator_ballots[ballot.node_name]
            if ballot == existing:
                return

            if ballot.has_different_ballot_id(existing):
                return

        if ballot.message_id in self.message_ids:
            self.log.debug('message already stored: %s', ballot.message)
            return

        from_outside = self.from_outside(ballot.node_name)
        self.log.debug(
            '[%s] [%s] receive ballot from %s(from_outside=%s)',
            self.node_name,
            self.state,
            ballot.node_name,
            from_outside,
        )

        if not from_outside:
            func = getattr(self, '_handle_%s' % self.state.name.lower())
            func(ballot)

        return

    def _handle_init(self, ballot):
        if self._is_new_ballot(ballot):
            self.broadcast(self.make_self_ballot(ballot))

        self.store(ballot)
        self._change_state_and_broadcasting(ballot)

    def _handle_sign(self, ballot):
        self.store(ballot)
        self._change_state_and_broadcasting(ballot)

    def _handle_accept(self, ballot):
        self.store(ballot)
        self._change_state_and_broadcasting(ballot)

        return

    def _handle_allconfirm(self, ballot):
        if not self._is_new_ballot(ballot):
            self.store(ballot)
        else:
            self.init()
            self.handle_ballot(ballot)

        return

    def _check_threshold_and_state(self):
        ballots = self.validator_ballots.values()
        state_consensus = None
        state_check_init = self.minimum
        state_check_sign = self.minimum
        state_check_accept = self.minimum
        self.log.debug('[%s] check_threshold: ballots=%s', self.node_name, ballots)

        for ballot in ballots:
            if ballot is None:
                continue

            if state_check_init < 1 or state_check_sign < 1 or state_check_accept < 1:
                break

            if self.state <= ballot.state:
                if ballot.state >= IsaacState.INIT:
                    state_check_init -= 1
                if ballot.state >= IsaacState.SIGN:
                    state_check_sign -= 1
                if ballot.state >= IsaacState.ACCEPT:
                    state_check_accept -= 1

            self.log.debug(
                '[%s] ballot.node_name=%s ballot.node_state= %s ',
                self.node_name,
                ballot.node_name,
                ballot.state,

            )

        self.log.info("state threshold check -- Isaac.INIT : %s , Isaac.SIGN: %s , Isaac.ACCEPT : %s",
                      state_check_init, state_check_sign, state_check_accept)

        check_threshold = [state_check_init, state_check_sign, state_check_accept]

        if check_threshold[0] < 1:
            state_consensus = IsaacState.SIGN

        if check_threshold[1] < 1:
            state_consensus = IsaacState.ACCEPT

        if check_threshold[2] < 1:
            state_consensus = IsaacState.ALLCONFIRM
        self.log.info('returning ballot state : %s', state_consensus)

        return state_consensus, check_threshold

    def _change_state_and_broadcasting(self, ballot):
        state = self._check_threshold_and_state()
        if state[0] is None:
            return

        state_init = state[1][0]
        state_sign = state[1][1]
        state_accept = state[1][2]

        self.log.debug("state change check : %s", state)
        if state_init < 1 or state_sign < 1 or state_accept < 1:
            self.set_state(state[0])
            if state[0] is IsaacState.ALLCONFIRM:
                self.save_message(ballot.message)

            self.broadcast(self.make_self_ballot(ballot))

        return
