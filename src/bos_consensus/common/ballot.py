import copy
import enum
import json

from ..consensus import get_fba_module
from ..util import get_uuid
from .message import Message

class Ballot:
    ballot_id = None
    node_name = None
    message = None
    state = None

    def __init__(self, ballot_id, node_name, message, state=None):
        assert isinstance(message, Message)
        if state is not None:
            assert isinstance(state, enum.IntEnum)
        self.ballot_id = ballot_id
        self.node_name = node_name
        self.message = message
        self.state = state

    def __repr__(self):
        return '<Ballot: ballot_id=%(ballot_id)s node_name=%(node_name)s state=%(state)s message=%(message)s' % self.__dict__  # noqa

    def __eq__(self, rhs):
        if rhs is None:
            return False
        assert isinstance(rhs, Ballot)
        return self.ballot_id == rhs.ballot_id and self.state == rhs.state and self.message == rhs.message  # noqa

    def has_different_ballot_id(self, rhs):
        if rhs is None:
            return False 
        assert isinstance(rhs, self.__class__)
        return self.ballot_id != rhs.ballot_id and self.state == rhs.state and self.message == rhs.message  # noqa

    def __copy__(self):
        return self.__class__(
            self.ballot_id,
            self.node_name,
            copy.copy(self.message),
            self.state,
        )

    def serialize(self, to_string=False):
        o = dict(
            ballot_id=self.ballot_id,
            node_name=self.node_name,
            message=self.message.serialize(to_string=False),
            state=self.state.name
        )

        if not to_string:
            return o

        return json.dumps(o)

    @classmethod
    def new(cls, node_name, message, state):
        assert isinstance(message, Message)

        return cls(
            get_uuid(),
            node_name,
            message,
            state,
        )

    @classmethod
    def from_string(cls, s):
        o = json.loads(s)

        state = get_fba_module('isaac').IsaacState

        return cls(
            o['ballot_id'],
            o['node_name'],
            Message.from_dict(o['message']),
            state[o['state']],
        )

    @property
    def message_id(self):
        return self.message.message_id