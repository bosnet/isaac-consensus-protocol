import asyncio
import time
import math
import hashlib
import json
from socket import socketpair
import urllib.parse
import uuid

from util import log


CLOCK_SEQ = int(time.time() * 1000000)


class Message:
    class InvalidMessageError(Exception):
        pass

    message_id = None
    hash_id = None
    data = None

    def __init__(self, node, message_id, hash_id, data):
        assert isinstance(data, str)
        assert message_id is not None
        assert hash_id == hashlib.sha1(data.encode()).hexdigest()

        self.node = node
        self.message_id = message_id
        self.hash_id = hash_id
        self.data = data

    def __repr__(self):
        d = self.__dict__.copy()
        d['data'] = d['data'] if len(d['data']) < 10 else (d['data'][:10] + '...')
        return '<Message: node=%(node)s message_id=%(message_id)s data=%(data)s>' % d

    def __eq__(self, message):
        if not isinstance(message, Message):
            return False

        if message.message_id != self.message_id:
            return False

        if message.hash_id != self.hash_id:
            return False

        if message.data != self.data:
            return False

        return True

    def copy(self):
        return self.__class__(
            self.node,
            self.message_id,
            self.hash_id,
            self.data,
        )

    def to_dict(self):
        return dict(
            message=self.to_message_dict(),
        )

    def to_message_dict(self):
        return dict(
            hash_id=self.hash_id,
            message_id=self.message_id,
            data=self.data,
        )

    def serialize(self, node):
        d = self.to_dict()
        d['node'] = node.name
        d['type_name'] = 'message'
        return json.dumps(d) + '\r\n\r\n'

    @classmethod
    def new(cls, data):
        assert isinstance(data, str)

        return cls(
            None,
            uuid.uuid1(clock_seq=CLOCK_SEQ).hex,
            hashlib.sha1(data.encode()).hexdigest(),
            data,
        )

    @classmethod
    def from_json(cls, data):
        try:
            o = json.loads(data)
        except json.decoder.JSONDecodeError as e:
            raise cls.InvalidMessageError(e)

        if 'type_name' not in o or o['type_name'] != 'message':
            raise cls.InvalidMessageError('`type_name` is not "message"')

        try:
            m = o['message']
            return cls(o['node'], m['message_id'], m['hash_id'], m['data'])
        except KeyError as e:
            raise cls.InvalidMessageError(e)

    @classmethod
    def from_dict(cls, o):
        m = o['message']
        return cls(o['node'], m['message_id'], m['hash_id'], m['data'])

    def get_message(self):
        return self


class Endpoint:
    scheme = None
    host = None
    port = None

    def __init__(self, scheme, host, port):
        self.scheme = scheme
        self.host = host
        self.port = port

    def __str__(self):
        return '<Endpoint: %(scheme)s://%(host)s:%(port)d>' % self.__dict__

    @classmethod
    def from_uri(cls, uri):
        parsed = urllib.parse.urlparse(uri)

        return cls(parsed.scheme, parsed.hostname, parsed.port)

    @property
    def uri(self):
        return '%(scheme)s://%(host)s:%(port)d' % self.__dict__

    def to_dict(self, simple=True):
        if simple:
            return '%(scheme)s://%(host)s:%(port)s' % self.__dict__

        return dict(
            scheme=self.scheme,
            host=self.host,
            port=self.port,
        )


class Quorum:
    validators = None
    threshold = None

    def __init__(self, threshold, validators):
        assert type(threshold) in (float, int)
        assert threshold <= 100 and threshold > 0  # threshold must be percentile
        assert len(
            list(filter(lambda x: not isinstance(x, Node), validators))
        ) < 1

        self.threshold = threshold
        self.validators = validators

    def __repr__(self):
        return '<Quorum: threshold=%(threshold)s validators=%(validators)s>' % self.__dict__

    def is_inside(self, node):
        return len(list(filter(lambda x: x.name == node.name, self.validators))) > 0

    def remove(self, node):
        if not self.is_inside(node):
            return

        self.validators = filter(lambda x: x != node, self.validators)

        return

    @property
    def minimum_quorum(self):
        '''
        the required minimum quorum will be round *up*
        '''
        return math.ceil((len(self.validators) + 1) * (self.threshold / 100))

    def to_dict(self, simple=True):
        return dict(
            validators=list(map(lambda x: x.to_dict(simple), self.validators)),
            threshold=self.threshold,
        )


class Node:
    name = None
    endpoint = None
    quorum = None

    def __init__(self, name, endpoint_string, quorum):
        self.name = name
        self.endpoint = Endpoint.from_uri(endpoint_string)
        if quorum is not None and quorum.is_inside(self):
            quorum.remove(self)

        self.quorum = quorum

    def __repr__(self):
        return '<Node: %s>' % self.name

    def __eq__(self, name):
        return self.name == name

    def to_dict(self, simple=True):
        return dict(
            name=self.name,
            endpoint=self.endpoint.to_dict(simple),
            quorum=self.quorum.to_dict(simple) if self.quorum is not None else None,
        )


class BaseTransport:
    name = None
    endpoint = None
    message_received_callback = None

    def __init__(self, name, endpoint):
        self.name = name
        self.endpoint = Endpoint.from_uri(endpoint)

    def receive(self, data):
        raise NotImplementedError()

    def write(self, data):
        raise NotImplementedError()

    def send(self, data):
        raise NotImplementedError()

    def start(self, message_received_callback):
        self.message_received_callback = message_received_callback

        return


LOCAL_TRANSPORT_LIST = dict(
)


class LocalTransportProtocol(asyncio.Protocol):
    transport = None

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        raise NotImplementedError()

    def connection_lost(self, exc):
        pass


class LocalTransport(BaseTransport):
    loop = None
    rsock = None
    wsock = None
    protocol = None

    buf = None
    data_delimeter = list('\r\n\r\n')

    def __init__(self, name, endpoint, loop):
        super(LocalTransport, self).__init__(name, endpoint)

        self.loop = loop
        self.buf = list()
        LOCAL_TRANSPORT_LIST[self.endpoint.uri] = self

    def start(self, *a, **kw):
        super(LocalTransport, self).start(*a, **kw)

        self.rsock, self.wsock = socketpair()

        conn = self.loop.create_connection(LocalTransportProtocol, sock=self.rsock)
        _, self.protocol = self.loop.run_until_complete(conn)
        self.protocol.data_received = self.data_receive

        return

    def data_receive(self, data):
        self.receive(data.decode())

        return

    def receive(self, data):
        log.transport.debug('%s: received: %s', self.name, data.encode())

        if '\r\n\r\n' not in data:
            self.buf.append(data)

            return

        messages = list()
        cr = list()
        sl = self.buf
        self.buf = list()
        for s in data:
            if s == self.data_delimeter[len(cr)]:
                cr.append(s)

                if self.data_delimeter == cr:
                    messages.append(''.join(sl))
                    cr = list()
                    sl = list()

                continue

            if len(cr) > 0 and s != self.data_delimeter[len(cr)]:
                s = ''.join(cr) + s
                cr = list()

            sl.append(s)

        if len(sl) > 0:
            self.buf.extend(sl)

        self.message_received_callback(messages)

        return

    def write(self, data):
        log.transport.debug('%s: wrote: %s', self.name, data.encode())

        return self.wsock.send(data.encode())

    def send(self, endpoint, data):
        assert isinstance(endpoint, Endpoint)

        log.transport.debug('%s: send: %s', self.name, data.strip().encode())

        LOCAL_TRANSPORT_LIST[endpoint.uri].write(data)

        return


class BaseServer:
    name = None
    transport = None

    def __init__(self, name, transport):
        self.name = name
        self.transport = transport

    def __str__(self):
        return '<Server: name=%(name)s>' % self.__dict__

    def start(self):
        log.server.debug('%s: trying to start server', self.name)

        self.transport.start(
            message_received_callback=self.message_receive,
        )

        log.server.debug('%s: server started', self.name)

        return

    def message_receive(self, data_list):
        log.server.debug('%s: received: %s', self.name, data_list)
