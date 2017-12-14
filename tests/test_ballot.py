from bos_consensus.ballot import Ballot
from bos_consensus.state import StateKind


def test_ballot():
    b = Ballot(1, 1, 'message', StateKind.INIT)
    assert b.ballot_num == 1
    assert b.node_id == 1
    assert b.message == 'message'
    assert b.node_state_kind == StateKind.INIT
