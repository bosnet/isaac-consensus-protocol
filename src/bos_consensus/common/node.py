from ..network import Endpoint


class Node:
    name = None
    endpoint = None

    def __init__(self, name, endpoint):
        assert isinstance(name, str)
        assert isinstance(endpoint, Endpoint)

        self.name = name
        self.endpoint = endpoint
        self.endpoint.update(name=name)

    def __eq__(self, b):
        assert isinstance(b, self.__class__)

        return self.endpoint == b.endpoint

    def __repr__(self):
        return '<Node: %s(%s)>' % (self.name, self.endpoint)

    def to_dict(self):
        return dict(
            name=self.name,
            endpoint=self.endpoint.serialize(),
        )

    def check_faulty(self):
        return False


def node_factory(name, endpoint, faulty_percent=0, faulty_kind=None):
    assert isinstance(endpoint, Endpoint)

    from .faulty_node import FaultyNode

    if faulty_percent == 0:
        return Node(name, endpoint)
    else:
        return FaultyNode(name, endpoint, faulty_percent, faulty_kind)
