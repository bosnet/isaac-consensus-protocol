import json
import logging
import os
import pathlib
import pprint  # noqa
import sys  # noqa
import threading
import time
import yaml

from bos_consensus.blockchain import Blockchain
from bos_consensus.common import node_factory
from bos_consensus.consensus import get_fba_module
from bos_consensus.network import Endpoint, get_network_module, BaseServer
from bos_consensus.util import (
    ArgumentParserShowDefaults,
    convert_dict_to_namedtuple,
    convert_json_config,
    convert_namedtuple_to_dict,
    get_free_port,
    get_local_ipaddress,
    logger,
)

from common import DivergentVotingConsensus
from audit import DivergentAuditor


AUDITING_TIMEOUT = 5  # 5 seconds


log = None

parser = ArgumentParserShowDefaults()
logger.set_argparse(parser)
parser.add_argument(
    'design',
    help='network design yaml or json',
    type=str,
)


CONSENSUS_MODULE = get_fba_module('isaac')


def load_design(filename):
    if not pathlib.Path(filename).exists():
        parser.error('file, `%s` does not exists.' % filename)

    if not pathlib.Path(filename).is_file():
        parser.error('file, `%s` is not valid file.' % filename)

    design = None

    with open(filename) as f:
        if filename.split('.')[-1] == 'yml':
            design = convert_dict_to_namedtuple(yaml.load(f.read()))
        elif filename.split('.')[-1] == 'json':
            temp_design = convert_json_config(json.load(f))
            design = convert_dict_to_namedtuple(temp_design)
        else:
            print('# error: \"file `%s` is not valid file. yml or json type is needed\"' % filename)
            sys.exit(1)

    network_module = get_network_module(design.common.network)

    nodes = dict()
    for name, config in design.nodes._asdict().items():
        port = getattr(config, 'port', None)
        if port is None:
            port = get_free_port()

        endpoint = Endpoint(network_module.SCHEME, get_local_ipaddress(), port, name=name)
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

    design_dict['common']['network_module'] = get_network_module(design.common.network)

    design_dict['nodes'] = list(nodes.values())
    design_dict['nodes_by_name'] = nodes
    return convert_dict_to_namedtuple(design_dict)


class NodeRunner(threading.Thread):
    def __init__(self, blockchain):
        super(NodeRunner, self).__init__()

        self.blockchain = blockchain

    def run(self):
        BaseServer(self.blockchain).start()

        return


if __name__ == '__main__':
    options = parser.parse_args()

    logger.from_argparse(logger, options)
    logger.set_level(logging.FATAL, 'http')
    logger.set_level(logging.FATAL, 'transport')

    design = load_design(options.design)

    log = logger.get_logger(__name__)
    log_state = logger.get_logger('consensus.state')

    log.info('network config loaded:\n%s', pprint.pformat(convert_namedtuple_to_dict(design), width=1))

    log.debug('trying to run %d / %d (faulty nodes / all nodes)', len(design.faulties), len(design.nodes))

    faulty_nodes = dict()
    blockchains = list()
    for node_design in design.nodes:
        name = node_design.node.name

        faulty_frequency = 0
        faulty = getattr(design.faulties, name, None)
        if faulty is not None:
            for case in faulty:
                if case.case.kind not in ('divergent_voting',):
                    continue

                faulty_frequency = int(case.case.frequency)

        faulty_nodes[name] = faulty_frequency

        if faulty_frequency > 0:
            consensus = DivergentVotingConsensus(
                faulty_frequency,
                node_design.node,
                node_design.quorum.threshold,
                node_design.quorum.validators,
            )
        else:
            consensus = CONSENSUS_MODULE.Consensus(
                node_design.node,
                node_design.quorum.threshold,
                node_design.quorum.validators,
            )

        transport = design.common.network_module.Transport(
            bind=(
                node_design.node.endpoint.host,
                node_design.node.endpoint.port,
            ),
        )
        blockchain = Blockchain(consensus, transport)

        blockchains.append(blockchain)

        NodeRunner(blockchain).start()
        DivergentAuditor(blockchain).start()

    prev = None
    while True:
        time.sleep(1)

        now = set(map(lambda x: (x.consensus.node.name, x.consensus.state), blockchains))
        if now == prev:
            continue

        prev = now
        for node_name, state in sorted(now):
            node_design = getattr(design.nodes_by_name, node_name)
            log_state.metric(
                node=node_name,
                state=state.name,
                faulty_frequency=faulty_nodes[node_name],
                quorum=dict(
                    threshold=node_design.quorum.threshold,
                    validators=list(map(lambda x: x.name, node_design.quorum.validators)),
                ),
            )
