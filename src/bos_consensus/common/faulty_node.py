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
    def get_faulty_kind(cls, faulty_kind_str):
        faulty_kind_dict = dict(
            node_unreachable=cls.NodeUnreachable,
            no_voting=cls.NoVoting,
            duplicated_message_sent=cls.DuplicatedMessageSent,
            divergent_voting=cls.DivergentVoting,
            state_regression=cls.StateRegression,
        )

        if faulty_kind_str not in faulty_kind_dict:
            return cls.Unknown
        else:
            return faulty_kind_dict[faulty_kind_str]


class FaultyNode(Node):
    faulty_kind = None
    faulty_percent = 0

    def __init__(self, name, address, faulty_kind_str, faulty_percent):
        super(FaultyNode, self).__init__(name, address)
        self.faulty_kind = FaultyNodeKind.get_faulty_kind(faulty_kind_str)
        self.faulty_percent = faulty_percent

    def check_faulty(self):
        return self.faulty_percent >= randint(1, 100)

    def __repr__(self):
        return ('<FaultyNode: name=%(name)s endpoint=%(endpoint)s faulty_kind=%(faulty_kind)s faulty_percent=%(faulty_percent)s]>' % self.__dict__)
