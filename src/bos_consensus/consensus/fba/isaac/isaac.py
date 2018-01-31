import enum

from bos_consensus.consensus.fba import FbaState, Fba
from bos_consensus.common.ballot import Ballot


class IsaacState(FbaState):
    NONE = enum.auto()
    INIT = enum.auto()
    SIGN = enum.auto()
    ACCEPT = enum.auto()
    ALLCONFIRM = enum.auto()


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
        if ballot.node_name in self.validators:
            existing = self.validators[ballot.node_name]['ballot']
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

        if self._check_threshold():
            self.set_state(IsaacState.SIGN)
            self.broadcast(self.make_self_ballot(ballot))

    def _handle_sign(self, ballot):
        self.store(ballot)

        if self._check_threshold():
            self.set_state(IsaacState.ACCEPT)
            self.broadcast(self.make_self_ballot(ballot))

    def _handle_accept(self, ballot):
        self.store(ballot)

        if self._check_threshold():
            self.set_state(IsaacState.ALLCONFIRM)  # [TODO]set_next_state
            self.save_message(ballot.message)
            self.broadcast(self.make_self_ballot(ballot))

        return

    def _handle_allconfirm(self, ballot):
        if self._is_new_ballot(ballot):
            self.init()
            self.handle_ballot(ballot)

        return

    def _check_threshold(self):
        ballots = list(map(lambda node: node['ballot'], self.validators.values()))
        validator_th = self.minimum

        for ballot in ballots:
            if ballot is None:
                continue

            if validator_th < 1:
                break

            if self.state <= ballot.state:
                validator_th -= 1

            self.log.debug(
                '[%s] ballot.node_name=%s validator_th=%s minimum_quorum=%s ballots=%s',
                self.node_name,
                ballot.node_name,
                validator_th,
                self.minimum,
                ballots,
            )

        return validator_th < 1
