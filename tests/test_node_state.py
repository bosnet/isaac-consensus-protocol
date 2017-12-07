from node import Node
from ballot import Ballot

def test_state_init_to_sign():
    node = Node(1, ('localhost', 5001), ['localhost:5002', 'localhost:5003'])
    assert str(node) == '<Node[INIT]: 1(http://localhost:5001)>'