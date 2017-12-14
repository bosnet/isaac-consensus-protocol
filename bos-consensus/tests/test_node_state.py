from node import Node
from ballot import Ballot
from statekind import StateKind
from state import (
    State,
    NoneState,
    SignState,
    InitState,
    AcceptState,
    AllConfirmState
)


def test_state_init():
    node = Node(1, ('localhost', 5001), 100, ['localhost:5002', 'localhost:5003'])
    assert node.node_id == 1
    assert node.node_state.kind == StateKind.NONE
    assert node.threshold == 100
    assert node.address == ('localhost', 5001)
    assert node.validator_addrs == ['localhost:5002', 'localhost:5003']


def test_state_init_to_sign():
    node1 = Node(1, ('localhost', 5001), 100, ['localhost:5002', 'localhost:5003'])

    node1.init_node()

    ballot = Ballot(1, 1, 'message', StateKind.INIT)

    node1.receive(ballot)

    assert node1.node_state.kind == StateKind.SIGN


def test_state_init_to_all_confirm_sequence():
    node1 = Node(1, ('localhost', 5001), 100, ['localhost:5002', 'localhost:5003'])
    node2 = Node(2, ('localhost', 5002), 100, ['localhost:5001', 'localhost:5003'])
    node3 = Node(3, ('localhost', 5003), 100, ['localhost:5001', 'localhost:5002'])

    node1.init_node()
    node2.init_node()
    node3.init_node()

    ballot_init_1 = Ballot(1, 1, 'message', StateKind.INIT)

    node1.receive(ballot_init_1)
    node2.receive(ballot_init_1)
    node3.receive(ballot_init_1)

    assert isinstance(node1.node_state, SignState)
    assert isinstance(node2.node_state, SignState)
    assert isinstance(node3.node_state, SignState)

    ballot_sign_1 = Ballot(1, 1, 'message', StateKind.SIGN)
    ballot_sign_2 = Ballot(1, 2, 'message', StateKind.SIGN)
    ballot_sign_3 = Ballot(1, 3, 'message', StateKind.SIGN)

    node1.receive(ballot_sign_1)
    node2.receive(ballot_sign_1)
    node3.receive(ballot_sign_1)

    node1.receive(ballot_sign_2)
    node2.receive(ballot_sign_2)
    node3.receive(ballot_sign_2)

    node1.receive(ballot_sign_3)
    node2.receive(ballot_sign_3)
    node3.receive(ballot_sign_3)

    assert isinstance(node1.node_state, AcceptState)
    assert isinstance(node2.node_state, AcceptState)
    assert isinstance(node3.node_state, AcceptState)

    ballot_accept_1 = Ballot(1, 1, 'message', StateKind.ACCEPT)
    ballot_accept_2 = Ballot(1, 2, 'message', StateKind.ACCEPT)
    ballot_accept_3 = Ballot(1, 3, 'message', StateKind.ACCEPT)

    node1.receive(ballot_accept_1)
    node1.receive(ballot_sign_1)    # different state ballot
    node2.receive(ballot_accept_1)
    node3.receive(ballot_accept_1)

    node1.receive(ballot_accept_2)
    node2.receive(ballot_accept_2)
    node3.receive(ballot_accept_2)

    node1.receive(ballot_accept_3)
    node2.receive(ballot_sign_3)    # different state ballot
    node3.receive(ballot_accept_3)

    assert isinstance(node1.node_state, AllConfirmState)
    assert isinstance(node2.node_state, AcceptState)
    assert isinstance(node3.node_state, AllConfirmState)


# def test_state_init_to_state_jump():
#     node1 = Node(1, ('localhost', 5001), 100, ['localhost:5002', 'localhost:5003'])
#     node2 = Node(2, ('localhost', 5002), 100, ['localhost:5001', 'localhost:5003'])
#     node3 = Node(3, ('localhost', 5003), 100, ['localhost:5001', 'localhost:5002'])

#     node1.init_node()
#     node2.init_node()
#     node3.init_node()

#     ballot_init_1 = Ballot(1, 1, 'message', StateKind.INIT)

#     node1.receive(ballot_init_1)
#     node2.receive(ballot_init_1)
#     node3.receive(ballot_init_1)

#     assert isinstance(node1.node_state, SignState)
#     assert isinstance(node2.node_state, SignState)
#     assert isinstance(node3.node_state, SignState)

#     ballot_sign_1 = Ballot(1, 1, 'message', StateKind.SIGN)
#     ballot_sign_2 = Ballot(1, 2, 'message', StateKind.ACCEPT)
#     ballot_sign_3 = Ballot(1, 3, 'message', StateKind.SIGN)

#     node1.receive(ballot_sign_1)
#     node2.receive(ballot_sign_1)
#     node3.receive(ballot_sign_1)

#     node1.receive(ballot_sign_2)
#     node2.receive(ballot_sign_2)
#     node3.receive(ballot_sign_2)

#     node1.receive(ballot_sign_3)
#     node2.receive(ballot_sign_3)
#     node3.receive(ballot_sign_3)

#     assert isinstance(node1.node_state, AcceptState)
#     assert isinstance(node2.node_state, AcceptState)
#     assert isinstance(node3.node_state, AcceptState)

#     ballot_accept_1 = Ballot(1, 1, 'message', StateKind.ACCEPT)
#     ballot_accept_2 = Ballot(1, 2, 'message', StateKind.ACCEPT)
#     ballot_accept_3 = Ballot(1, 3, 'message', StateKind.ACCEPT)

#     node1.receive(ballot_accept_1)
#     node1.receive(ballot_sign_1)    # different state ballot
#     node2.receive(ballot_accept_1)
#     node3.receive(ballot_accept_1)

#     node1.receive(ballot_accept_2)
#     node2.receive(ballot_accept_2)
#     node3.receive(ballot_accept_2)

#     node1.receive(ballot_accept_3)
#     node2.receive(ballot_sign_3)    # different state ballot
#     node3.receive(ballot_accept_3)

#     assert isinstance(node1.node_state, AllConfirmState)
#     assert isinstance(node2.node_state, AcceptState)
#     assert isinstance(node3.node_state, AllConfirmState)
