import copy
import json

from .consensus import get_consensus_module
from .message import Message
from .util import get_uuid


class Ballot:
    def __init__(self, ballot_id, node_id, message, node_state_kind):
        assert isinstance(message, Message)

        self.ballot_id = ballot_id
        self.node_id = node_id
        self.message = message
        self.node_state_kind = node_state_kind

    def __repr__(self):
        return '<Ballot: ballot_id=%(ballot_id)s node_id=%(node_id)s node_state_kind=%(node_state_kind)s message=%(message)s' % self.__dict__  # noqa

    def __eq__(self, a):
        return self.ballot_id == a.ballot_id and self.node_state_kind == a.node_state_kind and self.message == a.message  # noqa

    def has_different_ballot_id(self, a):
        assert isinstance(a, self.__class__)

        return self.ballot_id != a.ballot_id and self.node_state_kind == a.node_state_kind and self.message == a.message  # noqa

    def __copy__(self):
        return self.__class__(
            self.ballot_id,
            self.node_id,
            copy.copy(self.message),
            self.node_state_kind,
        )

    def serialize(self, node_id, to_string=False):
        o = dict(
            ballot_id=self.ballot_id,
            node_id=node_id,
            message=self.message.serialize(to_string=False),
            node_state_kind=self.node_state_kind.name
        )

        if not to_string:
            return o

        return json.dumps(o)

    @classmethod
    def new(cls, node_id, message, node_state_kind):
        assert isinstance(message, Message)

        return cls(
            get_uuid(),
            node_id,
            message,
            node_state_kind,
        )

    @classmethod
    def from_string(cls, s):
        o = json.loads(s)

        StateKind = get_consensus_module('simple_fba').StateKind

        return Ballot(
            o['ballot_id'],
            o['node_id'],
            Message.from_dict(o['message']),
            StateKind[o['node_state_kind']],
        )
