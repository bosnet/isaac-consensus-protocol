from .ballot import Ballot, BallotVotingResult
from ..consensus import get_fba_module
from .message import Message


class Slot:
    def __init__(self, slot_size):
        self.slot = dict()
        self.slot_size = slot_size
        self.timestamp_dict = dict()
        self.timestamp_list = list()
        self.last_ballot = None
        self.init_state = get_fba_module('isaac').IsaacState.INIT

        for i in range(slot_size):
            temp_name = 'b' + str(i)
            self.slot[temp_name] = Slot_element()

    def clear_all_validator_ballots(self):
        for k in self.slot.keys():
            self.slot[k].validator_ballots.clear()

    def find_empty_slot(self):
        for k in self.slot.keys():
            if self.slot[k].is_full is False:
                return k

    def get_ballot_state(self, ballot):
        return self.slot[self.get_ballot_index(ballot)].consensus_state

    def get_ballot_index(self, ballot):
        for k, v in self.slot.items():
            if v.is_full:
                if ballot.ballot_id == v.ballot.ballot_id:
                    return k
        return 'Not Found'

    def get_validator_ballots(self, ballot):
        return self.slot[self.get_ballot_index(ballot)].validator_ballots

    def check_full_and_insert_ballot(self, ballot):
        if self.is_empty():
            empty_slot_idx = self.find_empty_slot()
            self.insert_ballot(empty_slot_idx, ballot)
            return

        if not self.is_full():
            if ballot.ballot_id not in list(map(lambda x: x.ballot.ballot_id, self.slot.values())):
                empty_slot_idx = self.find_empty_slot()
                self.insert_ballot(empty_slot_idx, ballot)
                return

        else:
            if ballot.timestamp > self.timestamp_list[-1]:
                self.send_to_queue(ballot)
            elif ballot.timestamp == self.timestamp_list[-1] and ballot.ballot_id != self.last_ballot.ballot_id:
                self.send_to_queue(ballot)
            elif ballot.timestamp == self.timestamp_list[-1] and ballot.ballot_id == self.last_ballot.ballot_id:
                pass
            else:
                if self.slot[self.get_ballot_index(self.last_ballot)].consensus_state == get_fba_module('isaac').IsaacState.INIT:
                    self.send_to_queue(self.last_ballot)
                    if ballot.ballot_id not in list(map(lambda x: x.ballot.ballot_id, self.slot.values())):
                        empty_slot_idx = self.timestamp_dict[self.timestamp_list[-1]]
                        self.remove_ballot(self.slot[empty_slot_idx].ballot)
                        self.insert_ballot(empty_slot_idx, ballot)
                        return

    def insert_ballot(self, empty_slot_idx, ballot):
        self.slot[empty_slot_idx].add_ballot(ballot)
        self.timestamp_dict[ballot.timestamp] = empty_slot_idx
        self.timestamp_list.append(ballot.timestamp)
        self.sort_slot()

    def set_ballot_consensus_state(self, ballot, state):
        self.slot[self.get_ballot_index(ballot)].consensus_state = state

    def set_all_state(self, state):
        for k in self.slot.keys():
            self.slot[k].consensus_state = state

    def remove_ballot(self, ballot):
        self.slot[self.get_ballot_index(ballot)].remove_ballot()
        del self.timestamp_dict[ballot.timestamp]
        for i in range(len(self.timestamp_list) -1, -1, -1):
            if self.timestamp_list[i] == ballot.timestamp:
                del self.timestamp_list[i]
        self.sort_slot()

    def is_full(self):
        for k, _v in self.slot.items():
            if not self.slot[k].is_full:
                return False
        return True

    def is_empty(self):
        for k in self.slot.keys():
            if self.slot[k].is_full:
                return False
        return True

    def send_to_queue(self, ballot):
        pass

    def sort_slot(self):
        if not len(self.timestamp_list) < 1:
            self.timestamp_list.sort()
            self.last_ballot = self.slot[self.timestamp_dict[self.timestamp_list[-1]]].ballot
        return


class Slot_element:
    def __init__(self):
        self.ballot = Ballot(None, None, Message.new(None), get_fba_module('isaac').IsaacState.INIT)
        self.ballot.timestamp = None
        self.consensus_state = get_fba_module('isaac').IsaacState.INIT
        self.is_full = False
        self.validator_ballots = dict()

    def add_ballot(self, ballot):
        self.ballot = ballot
        self.consensus_state = get_fba_module('isaac').IsaacState.INIT
        self.is_full = True
        self.validator_ballots = dict()

    def remove_ballot(self):
        self.ballot = Ballot(None, None, Message.new(None), get_fba_module('isaac').IsaacState.INIT)
        self.ballot.timestamp = None
        self.consensus_state = None
        self.is_full = False
        self.validator_ballots = dict()
