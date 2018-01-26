import logging
import pprint  # noqa
import sys  # noqa
import threading
import yaml

from bos_consensus.blockchain import Blockchain
from bos_consensus.common.node import node_factory
from bos_consensus.consensus import get_fba_module
from bos_consensus.network import Endpoint, get_network_module, BaseServer
from bos_consensus.util import (
    ArgumentParserShowDefaults,
    convert_dict_to_namedtuple,
    convert_namedtuple_to_dict,
    get_free_port,
    get_local_ipaddress,
    logger,
)


log = None

parser = ArgumentParserShowDefaults()
parser.add_argument(
    'design',
    help='network design yaml',
    type=str,
)

log = None
logger.set_argparse(parser)


def load_design(filename):
    design = None

    with open(filename) as f:
        design = convert_dict_to_namedtuple(yaml.load(f.read()))

    network_module = get_network_module(design.common.network)

    nodes = dict()
    for name, config in design.nodes._asdict().items():
        endpoint = Endpoint(network_module.SCHEME, get_local_ipaddress(), get_free_port(), name=name)
        node = node_factory(name, endpoint, 0)

        if hasattr(config.quorum, 'threshold'):
            threshold = config.quorum.threshold
        else:
            threshold = design.common.threshold

        nodes[name] = dict(node=node, quorum=dict(validators=list(), threshold=threshold))

    for name, config in design.nodes._asdict().items():
        for node_name in config.quorum.validators:
            nodes[name]['quorum']['validators'].append(nodes[node_name]['node'])

    design_dict = convert_namedtuple_to_dict(design)

    design_dict['common']['consensus_module'] = get_fba_module(design.common.consensus)
    design_dict['common']['network_module'] = get_network_module(design.common.network)
    design_dict['nodes'] = nodes

    return convert_dict_to_namedtuple(design_dict)


class NodeRunner(threading.Thread):
    def __init__(self, node, threshold, validators, consensus_module, network_module):
        super(NodeRunner, self).__init__()

        self.node = node
        self.threshold = threshold
        self.validators = validators
        self.consensus_module = consensus_module
        self.network_module = network_module

    def run(self):
        consensus = self.consensus_module.Consensus(
            self.node,
            self.threshold,
            self.validators,
        )

        transport = self.network_module.Transport(bind=(self.node.endpoint.host, self.node.endpoint.port))

        blockchain = Blockchain(consensus, transport)
        base_server = BaseServer(blockchain)
        base_server.start()

        return


if __name__ == '__main__':
    options = parser.parse_args()

    logger.from_argparse(logger, options)
    logger.set_level(logging.FATAL, 'http')
    logger.set_level(logging.FATAL, 'transport')

    design = load_design(options.design)

    log = logger.get_logger(__name__)

    log.info('network config loaded:\n%s', pprint.pformat(convert_namedtuple_to_dict(design), width=1))

    log.debug('trying to run %d / %d (faulty nodes / all nodes)', len(design.faulties), len(design.nodes))

    for name, config in design.nodes._asdict().items():
        t = NodeRunner(
            config.node,
            config.quorum.threshold,
            config.quorum.validators,
            design.common.consensus_module,
            design.common.network_module,
        )
        t.start()
