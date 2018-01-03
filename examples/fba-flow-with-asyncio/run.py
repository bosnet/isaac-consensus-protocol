import json  # noqa
import time  # noqa
import argparse
import asyncio
import collections
import logging
import sys
from uuid import uuid1

from fba_consensus import Consensus
from network import (
    BaseServer,
    LocalTransport,
    Message,
    Node,
    Quorum,
)
from util import (
    log,
)


MESSAGE = None


async def check_message_in_storage(node):
    global MESSAGE

    if check_message_in_storage.is_running:
        return

    check_message_in_storage.is_running = True

    found = list()
    log.main.info('%s: checking input message was stored: %s', node.name, MESSAGE)
    while len(found) < len(servers):
        for node_name, server in servers.items():
            if node_name in found:
                continue

            storage = server.consensus.storage

            is_exists = storage.is_exists(MESSAGE)
            if is_exists:
                log.main.critical(
                    '> %s: is_exists=%s state=%s ballot=%s',
                    node_name,
                    is_exists,
                    server.consensus.ballot.state,
                    # json.dumps(storage.ballot_history.get(MESSAGE.message_id), indent=2),
                    '',  # json.dumps(storage.ballot_history.get(MESSAGE.message_id)),
                )
                found.append(node_name)

            await asyncio.sleep(0.01)

    await asyncio.sleep(3)

    check_message_in_storage.is_running = False

    MESSAGE = Message.new(uuid1().hex)
    servers['n0'].transport.send(nodes['n0'].endpoint, MESSAGE.serialize(client0_node))
    log.main.info('inject message %s -> n0: %s', client0_node.name, MESSAGE)

    return


check_message_in_storage.is_running = False


class TestConsensus(Consensus):
    def reached_all_confirm(self, ballot_message):
        asyncio.ensure_future(check_message_in_storage(self.node))

        return


class Server(BaseServer):
    node = None
    consensus = None

    def __init__(self, node, consensus, *a, **kw):
        assert isinstance(node, Node)
        assert isinstance(consensus, Consensus)

        super(Server, self).__init__(*a, **kw)

        self.node = node
        self.consensus = consensus

    def __repr__(self):
        return '<Server: node=%(node)s consensus=%(consensus)s>' % self.__dict__

    def message_receive(self, data_list):
        super(Server, self).message_receive(data_list)

        for i in data_list:
            log.server.debug('%s: hand over message to consensus: %s', self.name, i)
            self.consensus.receive(i)

        return


NodeConfig = collections.namedtuple(
    'NodeConfig',
    (
        'name',
        'endpoint',
        'threshold',
    ),
)


def check_threshold(v):
    v = int(v)
    if v < 1 or v > 100:
        raise argparse.ArgumentTypeError(
            '%d is an invalid thresdhold, it must be 0 < trs <= 100' % v,
        )

    return v


parser = argparse.ArgumentParser()
parser.add_argument('-s', dest='silent', action='store_true', help='turn off the debug messages')
parser.add_argument(
    '-nodes',
    type=int,
    default=4,
    help='number of validator nodes in the same quorum',
)
parser.add_argument('-trs', type=check_threshold, default=80, help='threshold')


if __name__ == '__main__':
    log_level = logging.DEBUG
    if '-s' in sys.argv[1:]:
        log_level = logging.INFO

    log.set_level(log_level)

    options = parser.parse_args()
    log.main.debug('options: %s', options)

    client0_config = NodeConfig('client0', None, None)
    client0_node = Node(client0_config.name, client0_config.endpoint, None)
    log.main.debug('client node created: %s', client0_node)
    client1_config = NodeConfig('client1', None, None)
    client1_node = Node(client1_config.name, client1_config.endpoint, None)
    log.main.debug('client node created: %s', client1_node)

    nodes_config = dict()
    for i in range(options.nodes):
        name = 'n%d' % i
        endpoint = 'sock://memory:%d' % i
        nodes_config[name] = NodeConfig(name, endpoint, options.trs)

    log.main.debug('node configs created: %s', nodes_config)

    quorums = dict()
    for name, config in nodes_config.items():
        validator_configs = filter(lambda x: x.name != name, nodes_config.values())

        quorums[name] = Quorum(
            config.threshold,
            list(map(lambda x: Node(x.name, x.endpoint, None), validator_configs)),
        )
    log.main.debug('quorums created: %s', quorums)

    nodes = dict()
    transports = dict()
    consensuses = dict()
    servers = dict()

    loop = asyncio.get_event_loop()

    for name, config in nodes_config.items():
        nodes[name] = Node(name, config.endpoint, quorums[name])
        log.main.debug('nodes created: %s', nodes)

        transports[name] = LocalTransport(name, config.endpoint, loop)
        log.main.debug('transports created: %s', transports)

        consensuses[name] = TestConsensus(nodes[name], quorums[name], transports[name])
        log.main.debug('consensuses created: %s', consensuses)

        servers[name] = Server(nodes[name], consensuses[name], name, transport=transports[name])
        log.main.debug('servers created: %s', servers)

    for server in servers.values():
        server.start()

    # send message to `server0`
    MESSAGE = Message.new(uuid1().hex)
    servers['n0'].transport.send(nodes['n0'].endpoint, MESSAGE.serialize(client0_node))
    log.main.info('inject message %s -> n0: %s', client0_node.name, MESSAGE)

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        log.main.debug('goodbye~')
        sys.exit(1)
    finally:
        loop.close()
