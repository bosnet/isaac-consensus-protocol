from ..consensus import get_fba_module
from .ballot import Ballot
from .slot import Slot
from .message import Message
from ..util import get_uuid


IsaacState = get_fba_module('isaac').IsaacState


def test_slot_size():
    slot_size = 3
    s0 = Slot(slot_size)

    assert len(s0.slot) == slot_size


def test_slot_elements_are_unique():
    slot_size = 3
    s0 = Slot(slot_size)

    assert len(set(s0.slot.keys())) == slot_size


def test_slot_insert_ballot():
    slot_size = 3
    s0 = Slot(slot_size)

    # this ballot will be inserted at `b0`
    b0 = Ballot(get_uuid(), 1, Message.new(get_uuid()), IsaacState.INIT)
    # this ballot will be inserted at `b1`
    b1 = Ballot(get_uuid(), 1, Message.new(get_uuid()), IsaacState.SIGN)

    s0.insert_ballot(s0.find_empty_slot(), b0)
    s0.insert_ballot(s0.find_empty_slot(), b1)

    assert s0.find_empty_slot() == 'b2'

    assert s0.slot[s0.get_ballot_index(b0)].ballot.ballot_id == b0.ballot_id
    assert s0.slot[s0.get_ballot_index(b1)].ballot.ballot_id == b1.ballot_id


def test_slot_check_state():
    slot_size = 3
    s0 = Slot(slot_size)

    # this ballot will be inserted at `b0`
    b0 = Ballot(get_uuid(), 1, Message.new(get_uuid()), IsaacState.INIT)
    # this ballot will be inserted at `b1`
    b1 = Ballot(get_uuid(), 1, Message.new(get_uuid()), IsaacState.SIGN)

    s0.insert_ballot(s0.find_empty_slot(), b0)
    s0.insert_ballot(s0.find_empty_slot(), b1)

    assert s0.get_ballot_state(b0) == IsaacState.INIT
    assert s0.get_ballot_state(b1) == IsaacState.INIT


def test_check_full_and_insert_ballot():
    slot_size = 3
    s0 = Slot(slot_size)

    # this ballot will be inserted at `b0`
    b0 = Ballot(get_uuid(), 1, Message.new(get_uuid()), IsaacState.INIT)
    # this ballot will be inserted at `b1`
    b1 = Ballot(get_uuid(), 1, Message.new(get_uuid()), IsaacState.SIGN)

    s0.check_full_and_insert_ballot(b0)
    assert s0.find_empty_slot() == 'b1'

    s0.check_full_and_insert_ballot(b1)
    assert s0.find_empty_slot() == 'b2'


def test_is_empty():
    slot_size = 3
    s0 = Slot(slot_size)

    assert s0.is_empty() is True

    # this ballot will be inserted at `b0`
    b0 = Ballot(get_uuid(), 1, Message.new(get_uuid()), IsaacState.INIT)

    s0.check_full_and_insert_ballot(b0)
    assert s0.is_empty() is False
    assert s0.is_full() is False


def test_is_full():
    slot_size = 2
    s0 = Slot(slot_size)

    assert s0.is_empty() is True

    # this ballot will be inserted at `b0`
    b0 = Ballot(get_uuid(), 1, Message.new(get_uuid()), IsaacState.INIT)
    b1 = Ballot(get_uuid(), 1, Message.new(get_uuid()), IsaacState.INIT)

    s0.check_full_and_insert_ballot(b0)
    s0.check_full_and_insert_ballot(b1)

    assert s0.is_empty() is False
    assert s0.is_full() is True


def test_clear_all_validator_ballots():
    slot_size = 2
    s0 = Slot(slot_size)

    assert s0.is_empty() is True

    # this ballot will be inserted at `b0`
    b0 = Ballot(get_uuid(), 1, Message.new(get_uuid()), IsaacState.INIT)
    b1 = Ballot(get_uuid(), 1, Message.new(get_uuid()), IsaacState.INIT)

    s0.check_full_and_insert_ballot(b0)
    s0.check_full_and_insert_ballot(b1)

    assert s0.is_empty() is False
    assert s0.is_full() is True

    s0.clear_all_validator_ballots()

    assert s0.is_empty() is False
    assert s0.is_full() is True

    s0.remove_ballot(b0)
    s0.remove_ballot(b1)

    assert s0.is_empty() is True
    assert s0.is_full() is False
