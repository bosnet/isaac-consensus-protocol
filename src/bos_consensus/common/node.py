import enum


class Node:
    name = None
    endpoint = None

    def __init__(self, name, endpoint):
        assert isinstance(name, str)

        self.name = name
        self.endpoint = endpoint

    def __eq__(self, rhs):
        assert isinstance(rhs, Node)
        rhs_endpoint = rhs.endpoint
        lhs_endpoint = self.endpoint

        t_str = '//localhost:'  # target_string
        r_str = '//127.0.0.1:'  # replace_string
        if t_str in rhs_endpoint:
            rhs_endpoint.replace(t_str, r_str)

        if t_str in lhs_endpoint:
            lhs_endpoint.replace(t_str, r_str)

        return lhs_endpoint == rhs_endpoint

    def __repr__(self):
        return '<Node: %s(%s)>' % (self.name, self.endpoint)

    def to_dict(self):
        return dict(
            name=self.name,
            endpoint=self.endpoint
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
    def __init__(self, name, address, faulty_percent):
        super(FaultyNode, self).__init__(name, address)
        self.faulty_percent = faulty_percent

    def check_faulty(self):
        from random import randint
        return self.faulty_percent >= randint(1, 100)


def node_factory(name, address, faulty_percent=0):
    assert type(address) in (list, tuple) and len(address) == 2
    assert type(address[0]) in (str,) and type(address[1]) in (int,)
    endpoint = 'http://%s:%s?name=%s' % (address[0], address[1], name)
    if faulty_percent == 0:
        return Node(name, endpoint)
    else:
        return FaultyNode(name, endpoint, faulty_percent)
