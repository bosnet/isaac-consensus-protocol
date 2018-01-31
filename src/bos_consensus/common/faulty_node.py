import enum
from random import randint

from bos_consensus.common.node import Node


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

    # faulty node kind for initialize
    Unknown = enum.auto()

    @classmethod
    def get_from_name(cls, s):
        if s not in FAULTY_KIND_NAMING_MAP:
            return cls.Unknown
        else:
            return FAULTY_KIND_NAMING_MAP[s]

    @classmethod
    def get_name(cls, s):
        for k, v in FAULTY_KIND_NAMING_MAP.items():
            if v == s:
                return k


FAULTY_KIND_NAMING_MAP = dict(
    node_unreachable=FaultyNodeKind.NodeUnreachable,
    no_voting=FaultyNodeKind.NoVoting,
    duplicated_message_sent=FaultyNodeKind.DuplicatedMessageSent,
    divergent_voting=FaultyNodeKind.DivergentVoting,
    state_regression=FaultyNodeKind.StateRegression,
)


class FaultyNode(Node):
    faulty_kind = None
    faulty_percent = 0

    def __init__(self, name, address, faulty_percent, faulty_kind_str):
        super(FaultyNode, self).__init__(name, address)
        self.faulty_kind = FaultyNodeKind.get_from_name(faulty_kind_str)
        self.faulty_percent = faulty_percent

    def check_faulty(self):
        return self.faulty_percent >= randint(1, 100)

    def __repr__(self):
        d = self.__dict__.copy()
        d['endpoint'] = self.endpoint.uri_full

        return ('<FaultyNode: name=%(name)s endpoint=%(endpoint)s faulty_kind=%(faulty_kind)s faulty_percent=%(faulty_percent)s]>' % d)  # noqa
