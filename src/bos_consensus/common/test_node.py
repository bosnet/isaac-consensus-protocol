from .node import node_factory
from ..network import Endpoint


def test_node():
    n1 = node_factory('n1', Endpoint.from_uri('http://localhost:5001'))

    assert n1.name == 'n1'
    assert n1.endpoint.uri_full == 'http://localhost:5001?name=n1'
    assert n1.to_dict() == {
        'endpoint': 'http://localhost:5001?name=n1',
        'name': 'n1',
    }
