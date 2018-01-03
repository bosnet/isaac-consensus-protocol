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
    consensus_module = get_consensus_module('simple_fba')
    node1 = Node(
        1,
        ('localhost', 5001),
        100,
        ['http://localhost:5002', 'http://localhost:5003'],
        consensus_module.Consensus(),
    )
    node1.init_node()

    StateKind = consensus_module.StateKind
    ballot_init_1 = Ballot(1, 1, 'message', StateKind.INIT)
    ballot_init_2 = Ballot(1, 2, 'message', StateKind.INIT)
    ballot_init_3 = Ballot(1, 3, 'message', StateKind.INIT)

    node1.receive_ballot(ballot_init_1)
    node1.receive_ballot(ballot_init_2)
    node1.receive_ballot(ballot_init_3)

    assert node1.consensus.node_state.kind == StateKind.SIGN


def test_state_init_to_all_confirm_sequence():
    consensus_module = get_consensus_module('simple_fba')
    StateKind = consensus_module.StateKind

    node1 = Node(
        1,
        ('localhost', 5001),
        100,
        ['http://localhost:5002', 'http://localhost:5003'],
        consensus_module.Consensus(),
    )
    node2 = Node(
        2,
        ('localhost', 5002),
        100,
        ['http://localhost:5001', 'http://localhost:5003'],
        consensus_module.Consensus(),
    )
    node3 = Node(
        3,
        ('localhost', 5003),
        100,
        ['http://localhost:5001', 'http://localhost:5002'],
        consensus_module.Consensus(),
    )

    node1.init_node()
    node2.init_node()
    node3.init_node()

    ballot_init_1 = Ballot(1, 1, 'message', StateKind.INIT)
    ballot_init_2 = Ballot(1, 2, 'message', StateKind.INIT)
    ballot_init_3 = Ballot(1, 3, 'message', StateKind.INIT)

    node1.receive_ballot(ballot_init_1)
    node1.receive_ballot(ballot_init_2)
    node1.receive_ballot(ballot_init_3)

    node2.receive_ballot(ballot_init_1)
    node2.receive_ballot(ballot_init_2)
    node2.receive_ballot(ballot_init_3)

    node3.receive_ballot(ballot_init_1)
    node3.receive_ballot(ballot_init_2)
    node3.receive_ballot(ballot_init_3)

    (
        SignState,
        AcceptState,
        AllConfirmState,
    ) = (
        consensus_module.SignState,
        consensus_module.AcceptState,
        consensus_module.AllConfirmState,
    )

    assert isinstance(node1.consensus.node_state, SignState)
    assert isinstance(node2.consensus.node_state, SignState)
    assert isinstance(node3.consensus.node_state, SignState)

    ballot_sign_1 = Ballot(1, 1, 'message', StateKind.SIGN)
    ballot_sign_2 = Ballot(1, 2, 'message', StateKind.SIGN)
    ballot_sign_3 = Ballot(1, 3, 'message', StateKind.SIGN)

    node1.receive_ballot(ballot_sign_1)
    node2.receive_ballot(ballot_sign_1)
    node3.receive_ballot(ballot_sign_1)

    node1.receive_ballot(ballot_sign_2)
    node2.receive_ballot(ballot_sign_2)
    node3.receive_ballot(ballot_sign_2)

    node1.receive_ballot(ballot_sign_3)
    node2.receive_ballot(ballot_sign_3)
    node3.receive_ballot(ballot_sign_3)

    assert isinstance(node1.consensus.node_state, AcceptState)
    assert isinstance(node2.consensus.node_state, AcceptState)
    assert isinstance(node3.consensus.node_state, AcceptState)

    ballot_accept_1 = Ballot(1, 1, 'message', StateKind.ACCEPT)
    ballot_accept_2 = Ballot(1, 2, 'message', StateKind.ACCEPT)
    ballot_accept_3 = Ballot(1, 3, 'message', StateKind.ACCEPT)

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

    assert isinstance(node1.consensus.node_state, AllConfirmState)
    assert isinstance(node2.consensus.node_state, AcceptState)
    assert isinstance(node3.consensus.node_state, AllConfirmState)


# def test_state_jump_from_init():
#     node1 = Node(1, ('localhost', 5001), 100, ['http://localhost:5002', 'http://localhost:5003'])

#     node1.init_node()

#     ballot_init_1 = Ballot(1, 1, 'message', StateKind.INIT)

#     node1.receive_ballot(ballot_init_1)

#     assert isinstance(node1.node_state, SignState)

#     ballot_sign_1 = Ballot(1, 1, 'message', StateKind.SIGN)
#     ballot_sign_2 = Ballot(1, 2, 'message', StateKind.ACCEPT)
#     ballot_sign_3 = Ballot(1, 3, 'message', StateKind.SIGN)

#     node1.receive_ballot(ballot_sign_1)
#     node1.receive_ballot(ballot_sign_2)
#     node1.receive_ballot(ballot_sign_3)

#     assert isinstance(node1.node_state, AcceptState)

#     ballot_accept_1 = Ballot(1, 1, 'message', StateKind.ACCEPT)
#     ballot_accept_2 = Ballot(1, 2, 'message', StateKind.ACCEPT)
#     ballot_accept_3 = Ballot(1, 3, 'message', StateKind.ACCEPT)

#     node1.receive_ballot(ballot_accept_1)
#     node1.receive_ballot(ballot_sign_1)    # different state ballot
#     node1.receive_ballot(ballot_accept_2)
#     node1.receive_ballot(ballot_accept_3)

#     assert isinstance(node1.node_state, AllConfirmState)
