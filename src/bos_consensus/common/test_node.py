from .node import node_factory


def test_node():
    n1 = node_factory('n1', ('localhost', 5001))

    assert n1.name == 'n1'
    assert n1.endpoint == 'http://localhost:5001?name=n1'
    assert n1.to_dict() == {
        'endpoint': 'http://localhost:5001?name=n1',
        'name': 'n1',
    }
