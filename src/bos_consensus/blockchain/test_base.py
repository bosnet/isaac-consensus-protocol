from ..blockchain.base import BaseBlockchain
from ..common.node import node_factory


def test_base():
    node = node_factory('n1', ('localhost', 5001))
    consensus = BaseBlockchain(node)

    assert consensus.node_name == 'n1'
    assert consensus.endpoint == 'http://localhost:5001?name=n1'
