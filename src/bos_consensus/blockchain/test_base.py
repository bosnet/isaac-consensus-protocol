from ..blockchain.base import BaseBlockchain
from ..common import node_factory
from ..network import Endpoint, get_network_module


def test_base():
    node = node_factory('n1', Endpoint.from_uri('http://localhost:5001'))
    Transport = get_network_module('default_http').Transport
    transport = Transport(
        bind=(
            '0.0.0.0',
            5001,
        ),
    )
    consensus = BaseBlockchain(node, transport)

    assert consensus.node_name == 'n1'
    assert consensus.endpoint.uri_full == 'http://localhost:5001?name=n1'
