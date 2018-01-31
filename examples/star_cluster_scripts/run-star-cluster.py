import json
import pathlib
import sys  # noqa
import threading

from bos_consensus.blockchain import Blockchain
from bos_consensus.consensus import get_fba_module
from bos_consensus.network import get_network_module, Endpoint, BaseServer
from bos_consensus.util import (
    ArgumentParserShowDefaults,
    get_local_ipaddress,
    logger,
)
from bos_consensus.common.node import node_factory
from star_cluster import (
    get_nodes,
    NodeInfo
)


parser = ArgumentParserShowDefaults()
parser.add_argument(
    '-i',
    '--input',
    required=True,
    help='Json format file that include node and quorum informations',
    type=str,
)

log = None
logger.set_argparse(parser)


def run_node(node_info):
    assert isinstance(node_info, NodeInfo)

    node = node_factory(
        node_info.name,
        Endpoint('http', get_local_ipaddress(), node_info.port),
        node_info.faulty_percent,
        node_info.faulty_kind,
    )
    consensus_module = get_fba_module('isaac')
    consensus = consensus_module.IsaacConsensus(
        node,
        node_info.threshold,
        node_info.validators,
    )

    network_module = get_network_module('default_http')
    transport = network_module.Transport(bind=('0.0.0.0', node_info.port))

    blockchain = Blockchain(consensus, transport)
    base_server = BaseServer(blockchain)
    base_server.start()


def run_all(nodes):
    assert isinstance(nodes, dict)
    for name, node_info in nodes.items():
        assert isinstance(node_info, NodeInfo)
        try:
            t = threading.Thread(target=run_node, args=(node_info,))
            t.start()
        except:  # noqa
            print('Error: unable to start thread')

    while 1:
        t.join()


def main(options):
    input_path = options.input
    if not pathlib.Path(input_path).exists():
        parser.error('json file, `%s` does not exists.' % input_path)

    if not pathlib.Path(input_path).is_file():
        parser.error('json file, `%s` is not valid file.' % input_path)

    with open(input_path) as input_data:
        data = json.load(input_data)

    nodes = get_nodes(data)
    run_all(nodes)


if __name__ == '__main__':
    options = parser.parse_args()

    logger.from_argparse(logger, options)
    log = logger.get_logger(__name__)

    log.debug('options: %s', options)
    log.debug('log settings: %s', logger.info)

    main(options)
