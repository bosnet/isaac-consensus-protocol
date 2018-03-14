import copy
import lorem
import json

from bos_consensus.util import get_uuid


class Message:
    message_id = None
    data = None

    def __init__(self, message_id, data):
        self.message_id = message_id
        self.data = data

    def __repr__(self):
        return '<Message: message_id=%(message_id)s data="%(data)s">' % self.__dict__

    def __eq__(self, a):
        return self.message_id == a.message_id and self.data == a.data

    def eq_id(self, rhs):
        return self.message_id == rhs.message_id

    def __copy__(self):
        return self.__class__(
            self.message_id,
            copy.copy(self.data),
        )

    def serialize(self, to_string=False):
        o = dict(
            message_id=self.message_id,
            data=self.data,
        )

        if not to_string:
            return o

        return json.dumps(o)

    @classmethod
    def new(cls, data=None):
        if data is None:
            data = '%s-%s' % (lorem.sentence().split()[0], get_uuid())

        return cls(
            get_uuid(),
            data=data,
        )

    @classmethod
    def from_string(cls, s):
        o = json.loads(s)

        return cls(
            o['message_id'],
            o['data'],
        )

    @classmethod
    def from_dict(cls, o):
        return cls(
            o['message_id'],
            o['data'],
        )
