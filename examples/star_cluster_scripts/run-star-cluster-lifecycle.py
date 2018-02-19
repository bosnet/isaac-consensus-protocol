import asyncio
import json
import logging
import pathlib
import sys  # noqa

from bos_consensus.blockchain import Blockchain
from bos_consensus.consensus import get_fba_module
from bos_consensus.network import Endpoint, get_network_module
from bos_consensus.util import (
    ArgumentParserShowDefaults,
    get_local_ipaddress,
    logger,
)
from bos_consensus.common import node_factory
from common import (
    get_nodes,
    NodeInfo,
    get_message_infos
)
from bos_consensus.common import Message


parser = ArgumentParserShowDefaults()
parser.add_argument(
    '-i',
    '--input',
    required=True,
    help='Json format file that include node and quorum information',
    type=str,
)
parser.add_argument(
    '-c',
    '--client',
    required=True,
    help='Json format file that include client messages information',
    type=str,
)


log = None
logger.set_argparse(parser)


async def send_message_coroutine(local_server, node_info, client_data):
    message_infos = get_message_infos(client_data)
    for message_info in message_infos:
        message_str = message_info[0]
        interval = message_info[1]
        message = Message.new(message_str)
        endpoint = Endpoint('local_socket', get_local_ipaddress(), node_info.port)
        log.debug(f'send message to {endpoint}')
        local_server.blockchain.transport.send(endpoint, message.serialize())
        await asyncio.sleep(interval * MS)


MS = 0.001


def run_all(node_data: dict, client_data: dict):
    assert isinstance(node_data, dict)
    assert isinstance(client_data, dict)

    nodes, scheme = get_nodes(node_data)
    assert isinstance(nodes, dict)
    loop = asyncio.get_event_loop()
    servers = dict()

    consensus_module = get_fba_module('isaac')
    network_module = get_network_module(scheme)

    for _, node_info in nodes.items():
        assert isinstance(node_info, NodeInfo)
        node = node_factory(
            node_info.name,
            Endpoint(scheme, get_local_ipaddress(), node_info.port),
            node_info.faulty_percent,
            node_info.faulty_kind,
        )

        consensus = consensus_module.Consensus(
            node,
            node_info.threshold,
            node_info.validators,
        )
        [consensus.add_to_validator_connected(node) for node in node_info.validators]

        transport = network_module.Transport(node, loop)

        blockchain = Blockchain(consensus, transport)
        servers[node.name] = network_module.Server(blockchain)

    for server in servers.values():
        server.start()

    try:
        local_server = list(servers.values())[0]
        node_info = list(nodes.values())[0]
        loop.run_until_complete(send_message_coroutine(local_server, node_info, client_data))
    except (KeyboardInterrupt, SystemExit):
        log.debug('exception occured!')
    finally:
        loop.close()

    for server in servers.values():
        log.info(server.blockchain.consensus.node)
        log.info(server.blockchain.consensus.messages)

    return


def main(options):
    input_path = options.input
    if not pathlib.Path(input_path).exists():
        parser.error('json file, `%s` does not exists.' % input_path)

    if not pathlib.Path(input_path).is_file():
        parser.error('json file, `%s` is not valid file.' % input_path)

    with open(input_path) as input_node_data:
        node_data = json.load(input_node_data)

    client_path = options.client
    if not pathlib.Path(client_path).exists():
        parser.error('json file, `%s` does not exists.' % client_path)

    if not pathlib.Path(client_path).is_file():
        parser.error('json file, `%s` is not valid file.' % client_path)

    with open(client_path) as input_client_data:
        client_data = json.load(input_client_data)

    run_all(node_data, client_data)

    return


if __name__ == '__main__':
    options = parser.parse_args()

    logger.from_argparse(logger, options)
    log = logger.get_logger(__name__)
    logger.set_level(logging.FATAL, 'http')
    logger.set_level(logging.FATAL, 'ping')

    log.debug('options: %s', options)
    log.debug('log settings: %s', logger.info)

    main(options)
