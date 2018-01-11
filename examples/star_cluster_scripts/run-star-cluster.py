import argparse
import colorlog
import json
import logging
import pathlib
import sys
import threading

from bos_consensus.consensus import get_consensus_module
from bos_consensus.network import get_network_module, BaseServer
from bos_consensus.node import Node
from bos_consensus.util import get_local_ipaddress
from star_cluster.star_cluster import (
    get_nodes,
    NodeInfo
)


logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

if sys.stdout.isatty():
    log_handler = colorlog.StreamHandler()
    log_handler.setFormatter(
        colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
        ),
    )

    logging.root.handlers = [log_handler]

log = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument(
    '-i',
    '--input',
    required=True,
    help='Json format file that include node and quorum informations',
    type=str,
)
parser.add_argument('-debug', help='debug log level', action='store_true')
parser.add_argument('-info', help='info log level', action='store_true')


def run_node(node_info):
    assert isinstance(node_info, NodeInfo)
    consensus_module = get_consensus_module('simple_fba')
    consensus = consensus_module.Consensus()

    nd = Node(
        node_info.id,
        (get_local_ipaddress(), node_info.port),
        node_info.threshold,
        node_info.validators,
        consensus,
    )

    network_module = get_network_module('default_http')
    transport = network_module.Transport(bind=('0.0.0.0', node_info.port))
    BaseServer(nd, transport).start()


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
    log_level = logging.ERROR

    if options.debug is True:
        log_level = logging.DEBUG
    if options.info is True:
        log_level = logging.INFO

    log.root.setLevel(log_level)
    logging.getLogger('http').setLevel(logging.ERROR)
    logging.getLogger('urllib3').setLevel(logging.ERROR)

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
    main(options)
