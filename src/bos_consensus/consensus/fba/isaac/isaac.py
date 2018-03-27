import collections
import enum
import threading

from bos_consensus.consensus.fba import FbaState, Fba
from bos_consensus.common import Ballot, BallotVotingResult, Slot

NOT_FOUND = Slot.NOT_FOUND


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

    def _handle_ballot(self, ballot):
        # filtering rules, for same `ballot_id` or `message_id`
        #  1. if `message_id` is already saved in `self.message_ids`, it will be passed
        #  1. if `ballot` is same,
        #       - same message
        #       - state
        #   it will be passed.
        #  1. if `ballot` is same except `ballot_id`, it will be passed
        assert isinstance(ballot, Ballot)

        if not self._is_valid_ballot(ballot):
            return

        func = getattr(
            self,
            '_handle_%s' % (
                self.get_ballot(ballot).consensus_state.name.lower() if self.slot.get_ballot_index(ballot) != NOT_FOUND else 'init',  # noqa
            ),
        )
        func(ballot)

        return

    def _is_valid_ballot(self, ballot):
        if ballot.message_id in self.message_ids:
            self.log.debug('message already stored: %s', ballot.message)
            return False

        if self.slot.has_diff_ballot_but_same_message(ballot):
            return False

        if self.slot.has_same_message_id_but_different_data(ballot):
            return False

        if self.slot.get_ballot_index(ballot) != NOT_FOUND:
            if ballot.ballot_id == self.get_ballot(ballot).ballot.ballot_id and ballot.timestamp != self.get_ballot(ballot).ballot.timestamp:
                return False

            if ballot.node_name in self.get_ballot(ballot).validator_ballots:
                existing = self.get_ballot(ballot).validator_ballots[ballot.node_name]
                if ballot == existing:
                    return False

                if ballot.has_different_ballot_id(existing):
                    return False

        from_outside = self.from_outside(ballot.node_name, ballot)
        if from_outside:
            return False

        return True

    def _handle_init(self, ballot):
        if self._is_new_ballot(ballot):
            self.slot.check_full_and_insert_ballot(ballot)
            self.log.metric(action='receive-new-ballot', ballot=ballot.serialize(to_string=False))
            new_ballot = self.make_self_ballot(ballot)
            if ballot._is_from_client():
                self.broadcast(new_ballot, 3)
            else:
                self.broadcast(new_ballot)
        self.store(ballot)
        self._check_slot_time(ballot)
        self._change_state_and_broadcasting(ballot)

    def _handle_sign(self, ballot):
        self.store(ballot)
        self._change_state_and_broadcasting(ballot)

    def _handle_accept(self, ballot):
        self.store(ballot)
        self._change_state_and_broadcasting(ballot)
        if self.slot.get_ballot_state(ballot) is IsaacState.ALLCONFIRM:
            self.save_message(ballot.message)
            self.slot.remove_ballot(ballot)
            if not self.slot.slot_queue.empty():
                ballots_in_queue = self.slot.slot_queue.get_nowait()
                self.slot.check_full_and_insert_ballot(ballots_in_queue)
                self.slot.slot_queue.task_done()

                return
        return

    def _handle_allconfirm(self, ballot):
        self.log.error('weired ballot found: %s', ballot.serialize(to_string=False))

        return

    def _check_threshold_and_state(self, ballot):
        ballots = self.get_ballot(ballot).validator_ballots.values() if (
                    self.slot.get_ballot_index(ballot) != NOT_FOUND) else list()
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

            if self.get_ballot(ballot).consensus_state <= ballot.state and ballot.result == BallotVotingResult.agree and ballot.message == self.get_ballot(ballot).ballot.message:
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

        self.log.metric(
            action='check-threshold',
            ballot=ballot.serialize(to_string=False),
            ballots=list(map(lambda x: x.serialize(to_string=False), ballots)),
            thresholds=collections.OrderedDict(
                init=state_check_init,
                sign=state_check_sign,
                accept=state_check_accept,
            ),
            next_state=state_consensus if state_consensus != self.slot.get_ballot_state(ballot) else None,
        )

        return state_consensus, check_threshold

    def _change_state_and_broadcasting(self, ballot):
        state = self._check_threshold_and_state(ballot)

        if state[0] is None:
            return

        state_init = state[1][0]
        state_sign = state[1][1]
        state_accept = state[1][2]

        self.log.debug("state change check : %s", state)
        if state_init < 1 or state_sign < 1 or state_accept < 1:
            self.set_state(ballot, state[0])

            if state[0] is not IsaacState.ALLCONFIRM:
                self.broadcast(self.make_self_ballot(ballot))

        return

    def _check_slot_time(self, ballot):
        timer = threading.Timer(60, self._remove_stuck_ballot, args=[ballot])
        timer.start()

    def _remove_stuck_ballot(self, ballot):
        if self.slot.get_ballot_index(ballot) != NOT_FOUND:
            if self._check_threshold_and_state(ballot) is not IsaacState.ALLCONFIRM:
                self.slot.remove_ballot(ballot)
                self.log.metric(action='remove-stuck-ballot', ballot=ballot.serialize(to_string=False))
