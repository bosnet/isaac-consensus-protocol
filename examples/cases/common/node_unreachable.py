import random
import time

from bos_consensus.network import get_network_module
from bos_consensus.util import (
    logger,
)


NETWORK_MODULE = get_network_module('default_http')


class NodeUnreachableBOSNetHTTPServer(NETWORK_MODULE.BOSNetHTTPServer):
    no_response_started_time = None

    def __init__(self, *a, **kw):
        super(NodeUnreachableBOSNetHTTPServer, self).__init__(*a, **kw)

        self.no_response_started_time = None


class NodeUnreachableBOSNetHTTPServerRequestHandler(NETWORK_MODULE.BOSNetHTTPServerRequestHandler):
    faulty = None

    def __init__(self, node_name, *a, **kw):
        self.log_node_unreachable = logger.get_logger('http.node-unreachable', node=node_name)

        super(NodeUnreachableBOSNetHTTPServerRequestHandler, self).__init__(node_name, *a, **kw)

    def _parse_request(self):
        query, parsed = super(NodeUnreachableBOSNetHTTPServerRequestHandler, self)._parse_request()

        if self._check_no_response():
            self.log.metric(action='faulty-node', fault_type='node_unreachable')
            return (None, None)

        return (query, parsed)

    def _check_no_response(self):
        if self.faulty.frequency == 0:
            return False

        if self.faulty.frequency == 100:
            return True

        if self.server.no_response_started_time is not None:
            if self.server.no_response_started_time > (time.time() - self.faulty.duration):
                return True

            self.log_node_unreachable.info(
                'no-response ended: last-started=%d elapsed=%d duration=%d',
                self.server.no_response_started_time,
                time.time() - self.server.no_response_started_time,
                self.faulty.duration,
            )
            self.server.no_response_started_time = None

            return False

        r = random.randint(0, 100)
        if r <= self.faulty.frequency:
            self.server.no_response_started_time = time.time()
            self.log_node_unreachable.info(
                'no-response started: choice=%d frequency=%d duration=%d',
                r,
                self.faulty.frequency,
                self.faulty.duration,
            )

            return True

        return False


class NodeUnreachableTransport(NETWORK_MODULE.Transport):
    http_server_class = NodeUnreachableBOSNetHTTPServer

    def __init__(self, faulty, **config):
        self.__class__.http_request_handler_class = type(
            'NodeUnreachableBOSNetHTTPServerRequestHandler-frequency=%s-duration=%s' % (
                faulty.frequency,
                faulty.duration,
            ),
            (NodeUnreachableBOSNetHTTPServerRequestHandler,),
            dict(faulty=faulty),
        )

        super(NodeUnreachableTransport, self).__init__(**config)
