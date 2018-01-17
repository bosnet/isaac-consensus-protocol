from .. import get_consensus_module
from ...ballot import Ballot
from ...node import Node


def test_state_init():
    consensus_module = get_consensus_module('simple_fba')
    node = Node(
        1,
        ('localhost', 5001),
        100,
        ['http://localhost:5002', 'http://localhost:5003'],
        consensus_module.Consensus(),
    )
    assert node.node_id == 1

    assert node.consensus.node_state.kind == consensus_module.StateKind.NONE
    assert node.threshold == 100
    assert node.address == ('localhost', 5001)
    assert not node.validators['http://localhost:5002']
    assert not node.validators['http://localhost:5003']


def stub_func(_, __):
    return


Node.broadcast = stub_func


def test_state_init_to_sign():
    node_id_1 = 'http://localhost:5001'
    node_id_2 = 'http://localhost:5002'
    node_id_3 = 'http://localhost:5003'

    consensus_module = get_consensus_module('simple_fba')
    node1 = Node(
        node_id_1,
        ('localhost', 5001),
        100,
        [node_id_2, node_id_3],
        consensus_module.Consensus(),
    )
    node1.init_node()

    StateKind = consensus_module.StateKind
    ballot_init_1 = Ballot(1, node_id_1, 'message', StateKind.INIT)
    ballot_init_2 = Ballot(1, node_id_2, 'message', StateKind.INIT)
    ballot_init_3 = Ballot(1, node_id_3, 'message', StateKind.INIT)

    node1.receive_ballot(ballot_init_1)
    node1.receive_ballot(ballot_init_2)
    node1.receive_ballot(ballot_init_3)

    assert node1.consensus.node_state.kind == StateKind.SIGN


def test_state_init_to_all_confirm_sequence():
    node_id_1 = 'http://localhost:5001'
    node_id_2 = 'http://localhost:5002'
    node_id_3 = 'http://localhost:5003'

    consensus_module = get_consensus_module('simple_fba')
    StateKind = consensus_module.StateKind

    node1 = Node(
        node_id_1,
        ('localhost', 5001),
        100,
        [node_id_2, node_id_3],
        consensus_module.Consensus(),
    )
    node2 = Node(
        node_id_2,
        ('localhost', 5002),
        100,
        [node_id_1, node_id_3],
        consensus_module.Consensus(),
    )
    node3 = Node(
        node_id_1,
        ('localhost', 5003),
        100,
        [node_id_1, node_id_2],
        consensus_module.Consensus(),
    )

    node1.init_node()
    node2.init_node()
    node3.init_node()

    ballot_init_1 = Ballot(1, node_id_1, 'message', StateKind.INIT)
    ballot_init_2 = Ballot(1, node_id_2, 'message', StateKind.INIT)
    ballot_init_3 = Ballot(1, node_id_3, 'message', StateKind.INIT)

    node1.receive_ballot(ballot_init_1)
    node1.receive_ballot(ballot_init_2)
    node1.receive_ballot(ballot_init_3)

    node2.receive_ballot(ballot_init_1)
    node2.receive_ballot(ballot_init_2)
    node2.receive_ballot(ballot_init_3)

    node3.receive_ballot(ballot_init_1)
    node3.receive_ballot(ballot_init_2)
    node3.receive_ballot(ballot_init_3)

    assert isinstance(node1.consensus.node_state, consensus_module.SignState)
    assert isinstance(node2.consensus.node_state, consensus_module.SignState)
    assert isinstance(node3.consensus.node_state, consensus_module.SignState)

    ballot_sign_1 = Ballot(1, node_id_1, 'message', StateKind.SIGN)
    ballot_sign_2 = Ballot(1, node_id_2, 'message', StateKind.SIGN)
    ballot_sign_3 = Ballot(1, node_id_3, 'message', StateKind.SIGN)

    node1.receive_ballot(ballot_sign_1)
    node2.receive_ballot(ballot_sign_1)
    node3.receive_ballot(ballot_sign_1)

    node1.receive_ballot(ballot_sign_2)
    node2.receive_ballot(ballot_sign_2)
    node3.receive_ballot(ballot_sign_2)

    node1.receive_ballot(ballot_sign_3)
    node2.receive_ballot(ballot_sign_3)
    node3.receive_ballot(ballot_sign_3)

    assert isinstance(node1.consensus.node_state, consensus_module.AcceptState)
    assert isinstance(node2.consensus.node_state, consensus_module.AcceptState)
    assert isinstance(node3.consensus.node_state, consensus_module.AcceptState)

    ballot_accept_1 = Ballot(1, node_id_1, 'message', StateKind.ACCEPT)
    ballot_accept_2 = Ballot(1, node_id_2, 'message', StateKind.ACCEPT)
    ballot_accept_3 = Ballot(1, node_id_3, 'message', StateKind.ACCEPT)

    node1.receive_ballot(ballot_accept_1)
    node1.receive_ballot(ballot_sign_1)    # different state ballot
    node2.receive_ballot(ballot_accept_1)
    node3.receive_ballot(ballot_accept_1)

    node1.receive_ballot(ballot_accept_2)
    node2.receive_ballot(ballot_accept_2)
    node3.receive_ballot(ballot_accept_2)

    node1.receive_ballot(ballot_accept_3)
    node2.receive_ballot(ballot_sign_3)    # different state ballot
    node3.receive_ballot(ballot_accept_3)

    assert isinstance(node1.consensus.node_state, consensus_module.AllConfirmState)
    assert isinstance(node2.consensus.node_state, consensus_module.AcceptState)
    assert isinstance(node3.consensus.node_state, consensus_module.AllConfirmState)


def test_state_jump_from_init():
    node_id_1 = 'http://localhost:5001'
    node_id_2 = 'http://localhost:5002'
    node_id_3 = 'http://localhost:5003'
    node_id_4 = 'http://localhost:5004'

    consensus_module = get_consensus_module('simple_fba')
    state_kind = consensus_module.StateKind
    node1 = Node(
        node_id_1,
        ('localhost', 5001),
        100,
        [node_id_2, node_id_3, node_id_4],
        consensus_module.Consensus(),
    )

    node1.init_node()

    ballot_init_2 = Ballot(1, node_id_2, 'message', state_kind.INIT)
    ballot_init_3 = Ballot(1, node_id_3, 'message', state_kind.INIT)
    ballot_init_4 = Ballot(1, node_id_4, 'message', state_kind.INIT)

    node1.receive_ballot(ballot_init_2)
    node1.receive_ballot(ballot_init_3)
    node1.receive_ballot(ballot_init_4)

    assert isinstance(node1.consensus.node_state, consensus_module.SignState)

    ballot_sign_2 = Ballot(1, node_id_2, 'message', state_kind.ACCEPT)
    ballot_sign_3 = Ballot(1, node_id_3, 'message', state_kind.SIGN)
    ballot_sign_4 = Ballot(1, node_id_4, 'message', state_kind.SIGN)

    node1.receive_ballot(ballot_sign_2)
    node1.receive_ballot(ballot_sign_3)
    node1.receive_ballot(ballot_sign_4)

    assert isinstance(node1.consensus.node_state, consensus_module.AcceptState)

    ballot_accept_3 = Ballot(1, node_id_3, 'message', state_kind.ACCEPT)
    ballot_accept_4 = Ballot(1, node_id_4, 'message', state_kind.ACCEPT)

    node1.receive_ballot(ballot_accept_3)
    node1.receive_ballot(ballot_accept_4)

    assert isinstance(node1.consensus.node_state, consensus_module.AllConfirmState)
