import asyncio
from socket import socketpair
import json

from ..base import (
    Endpoint,
    BaseServer,
    BaseTransport,
)
from bos_consensus.common import Ballot, Message, Node

SCHEME = 'socket'

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


class Transport(BaseTransport):
    node_name = None
    endpoint = None
    loop = None
    rsock = None
    wsock = None
    buf = None
    data_delimeter = list('\r\n\r\n')

    def __init__(self, node: Node, loop):
        super(Transport, self).__init__()
        self.node_name = node.name
        self.endpoint = node.endpoint
        self.loop = loop
        self.buf = list()

        LOCAL_TRANSPORT_LIST[self.endpoint.uri] = self

    def _start(self):
        self.rsock, self.wsock = socketpair()
        conn = self.loop.create_connection(LocalTransportProtocol, sock=self.rsock)
        _, self.protocol = self.loop.run_until_complete(conn)
        self.protocol.data_received = self.data_receive

        self.log.debug('[%s] transport started', self.node_name)

        return

    def data_receive(self, data):
        self.receive(data.decode())

        return

    def receive(self, data):
        self.log.debug('[%s] received: %r', self.node_name, data)

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
        self.log.debug('[%s]: wrote: %s', self.node_name, data.encode())

        return self.wsock.send(data.encode())

    def send(self, endpoint, data, retries=None):
        assert isinstance(endpoint, Endpoint)
        if retries is None:
            retries = 1

        node_name = self.blockchain.node_name
        self.log.debug('[%s] begin send_to %s' % (node_name, endpoint))
        data_str = json.dumps(data) + '\r\n\r\n'

        n = 0
        while n < retries:
            try:
                LOCAL_TRANSPORT_LIST[endpoint.uri].write(data_str)
            except Exception as e:
                self.log.error('failed to send: tries=%d data=%s to=%s: %s', n, data, endpoint, e)
                n += 1
                continue
            else:
                self.log.debug('successfully sent data=%s to=%s', data, endpoint)
                return True

        self.log.error('max retries, %d exceeded: data=%r to=%r', retries, data, endpoint)

        return False

    def set_requests(self):
        pass


class LocalSocketServer(BaseServer):
    def message_received_callback(self, data_list):
        for data in data_list:
            if 'ballot_id' in data:
                ballot = Ballot.from_string(data)
                self.blockchain.receive_ballot(ballot)
            elif 'message_id' in data:
                message = Message.from_string(data)
                self.blockchain.receive_message_from_client(message)
            else:
                pass
