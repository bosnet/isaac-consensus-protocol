from ..consensus import get_fba_module
from .ballot import Ballot
from .message import Message
from ..util import get_uuid


def test_ballot():
    IsaacState = get_fba_module('isaac').IsaacState

    ballot_id = get_uuid()

    message = Message.new('message')

    b = Ballot(ballot_id, 1, message, IsaacState.INIT)
    assert b.ballot_id == ballot_id
    assert b.node_name == 1
    assert b.message == message
    assert b.state == IsaacState.INIT
