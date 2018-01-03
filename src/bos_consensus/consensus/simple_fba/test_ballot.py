from ...ballot import Ballot
from .. import get_consensus_module


def test_ballot():
    StateKind = get_consensus_module('simple_fba').StateKind

    b = Ballot(1, 1, 'message', StateKind.INIT)
    assert b.ballot_num == 1
    assert b.node_id == 1
    assert b.message == 'message'
    assert b.node_state_kind == StateKind.INIT
