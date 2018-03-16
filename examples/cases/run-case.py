import asyncio
import logging
import os
import pathlib
import pprint  # noqa
import sys  # noqa
import time

from bos_consensus.blockchain import Blockchain
from bos_consensus.consensus import get_fba_module
from bos_consensus.network import get_network_module
from bos_consensus.util import (
    ArgumentParserShowDefaults,
    convert_dict_to_namedtuple,
    convert_json_config,
    convert_namedtuple_to_dict,
    get_free_port,
    get_local_ipaddress,
    get_module,
    logger,
)

from common import (
    FaultyBlockchain,
    load_design,
    NodeRunner,
)
from common.audit import FaultyNodeAuditor


CONSENSUS_MODULE = get_fba_module('isaac')


parser = ArgumentParserShowDefaults()
logger.set_argparse(parser)
parser.add_argument(
    '-case',
    help='set the case name',
    default=None,
    type=str,
)

parser.add_argument(
    'design',
    help='design should be yaml or json',
    type=str,
)


def run(options, design):
    network_module = get_network_module('default_http')
    blockchains = list()
    loop = asyncio.get_event_loop()
    auditors = dict()
    for node_design in design.nodes:
        node = node_design.node
        consensus = CONSENSUS_MODULE.Consensus(
            node_design.node,
            node_design.quorum.threshold,
            node_design.quorum.validators,
        )

        transport = network_module.Transport(bind=('0.0.0.0', node_design.node.endpoint.port))
        faulties = getattr(design.faulties, node_design.node.name, list())
        if len(faulties) > 0:
            blockchain = FaultyBlockchain(faulties, consensus, transport)
        else:
            blockchain = Blockchain(consensus, transport)

        blockchains.append(blockchain)

        NodeRunner(blockchain).start()
        auditors[node.name] = FaultyNodeAuditor(blockchain, loop, 3)

    [asyncio.ensure_future(auditor.start()) for auditor in auditors.values()]

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        log.debug('exception occured!')

    return blockchains


if __name__ == '__main__':
    options = parser.parse_args()

    logger.from_argparse(logger, options)
    logger.set_level(logging.FATAL, 'http')
    logger.set_level(logging.FATAL, 'transport')

    filename = options.design
    if not pathlib.Path(filename).exists():
        parser.error('file, `%s` does not exists.' % filename)

    if not pathlib.Path(filename).is_file():
        parser.error('file, `%s` is not valid file.' % filename)

    design = load_design(filename)

    log = logger.get_logger(__name__)
    log_state = logger.get_logger('consensus.state')

    log.info('design loaded:\n%s', pprint.pformat(convert_namedtuple_to_dict(design), width=1))

    log.debug('trying to run %d / %d (faulty nodes / all nodes)', len(design.faulties), len(design.nodes))

    run_func = run
    if options.case is not None:
        try:
            os.chdir(pathlib.Path(options.case).absolute())
            sys.path.insert(0, '.')

            run_func = getattr(get_module('main'), 'run', None)
        except (FileNotFoundError, AttributeError):
            log.debug('failed to load case, %s', options.case)
        else:
            log.debug('loaded case from %s', options.case)

    blockchains = run_func(options, design)

    prev = None
    while True:
        time.sleep(1)

        now = set(map(lambda x: (x.consensus.node.name, x.consensus.state), blockchains))
        if now == prev:
            continue

        prev = now
        for node_name, state in sorted(now):
            node_design = getattr(design.nodes_by_name, node_name)
            faulties = getattr(design.faulties, node_design.node.name, list())
            log_state.metric(
                node=node_name,
                state=state.name,
                faulties=faulties,
                quorum=dict(
                    threshold=node_design.quorum.threshold,
                    validators=list(map(lambda x: x.name, node_design.quorum.validators)),
                ),
            )
