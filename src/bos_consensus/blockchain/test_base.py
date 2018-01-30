from ..blockchain.base import BaseBlockchain
from ..common.node import node_factory
from ..network import Endpoint


def test_base():
    node = node_factory('n1', Endpoint.from_uri('http://localhost:5001'))
    consensus = BaseBlockchain(node)

    assert consensus.node_name == 'n1'
    assert consensus.endpoint.uri_full == 'http://localhost:5001?name=n1'
