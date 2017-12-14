from bos_consensus.node import Node
from bos_consensus.ballot import Ballot
from bos_consensus.state import InitState
from bos_consensus.state import SignState
from bos_consensus.state import AcceptState
from bos_consensus.state import AllConfirmState


def test_state_init():
    node = Node(1, ('localhost', 5001), 100, ['localhost:5002', 'localhost:5003'])
    assert node.node_id == 1
    assert isinstance(node.node_state, InitState)
    assert node.threshold == 100
    assert node.address == ('localhost', 5001)
    assert node.validators == ['localhost:5002', 'localhost:5003']


def test_state_init_to_sign():
    node1 = Node(1, ('localhost', 5001), 100, ['localhost:5002', 'localhost:5003'])
    node2 = Node(2, ('localhost', 5002), 100, ['localhost:5001', 'localhost:5003'])
    node3 = Node(3, ('localhost', 5003), 100, ['localhost:5001', 'localhost:5002'])

    ballot = Ballot(1, 1, 'message', node1.node_state)

    node1.receive(ballot)

    assert isinstance(node1.node_state, SignState)


def test_state_init_to_all_confirm():
    node1 = Node(1, ('localhost', 5001), 100, ['localhost:5002', 'localhost:5003'])
    node2 = Node(2, ('localhost', 5002), 100, ['localhost:5001', 'localhost:5003'])
    node3 = Node(3, ('localhost', 5003), 100, ['localhost:5001', 'localhost:5002'])

    ballot_init_1 = Ballot(1, 1, 'message', node1.node_state)

    node1.receive(ballot_init_1)
    node2.receive(ballot_init_1)
    node3.receive(ballot_init_1)

    assert isinstance(node1.node_state, SignState)
    assert isinstance(node2.node_state, SignState)
    assert isinstance(node3.node_state, SignState)

    ballot_sign_1 = Ballot(1, 1, 'message', node1.node_state)
    ballot_sign_2 = Ballot(1, 2, 'message', node2.node_state)
    ballot_sign_3 = Ballot(1, 3, 'message', node3.node_state)

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

    ballot_accept_1 = Ballot(1, 1, 'message', node1.node_state)
    ballot_accept_2 = Ballot(1, 2, 'message', node2.node_state)
    ballot_accept_3 = Ballot(1, 3, 'message', node3.node_state)

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
