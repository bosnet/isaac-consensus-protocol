import enum
from random import randint

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


class FaultyNodeKind(enum.Enum):
    # failed to connect to the node or failed to get the proper response from
    # the node.
    NodeUnreachable = enum.auto()

    # in single phase of consensus, the node does not send voting messages.
    NoVoting = enum.auto()

    # the node sends the duplicated, but same messages.
    DuplicatedMessageSent = enum.auto()

    # in single phase of consensus, the node sends different voting with the
    # other nodes on the same message.
    DivergentVoting = enum.auto()

    # the node broadcasts some state of ballot, but he sends again with the
    # previous state of ballot.
    StateRegression = enum.auto()


class FaultyNode(Node):
    def __init__(self, name, endpoint, faulty_percent):
        super(FaultyNode, self).__init__(name, endpoint)
        self.faulty_percent = faulty_percent

    def check_faulty(self):
        return self.faulty_percent >= randint(1, 100)


def node_factory(name, endpoint, faulty_percent=0):
    assert isinstance(endpoint, Endpoint)

    if faulty_percent == 0:
        return Node(name, endpoint)
    else:
        return FaultyNode(name, endpoint, faulty_percent)
