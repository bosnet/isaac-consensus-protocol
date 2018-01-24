from .. import get_consensus_module
from ...ballot import Ballot
from ...message import Message
from ...util import get_uuid


def test_ballot():
    StateKind = get_consensus_module('simple_fba').StateKind

    ballot_id = get_uuid()

    message = Message.new('message')

    b = Ballot(ballot_id, 1, message, StateKind.INIT)
    assert b.ballot_id == ballot_id
    assert b.node_id == 1
    assert b.message == message
    assert b.node_state_kind == StateKind.INIT
