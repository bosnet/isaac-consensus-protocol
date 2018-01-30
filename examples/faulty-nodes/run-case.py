import logging
import os
import pathlib
import pprint  # noqa
import sys  # noqa
import time

from bos_consensus.blockchain import Blockchain
from bos_consensus.consensus import get_fba_module
from bos_consensus.util import (
    ArgumentParserShowDefaults,
    convert_namedtuple_to_dict,
    get_module,
    logger,
)

from common import (
    FaultyBlockchain,
    load_design,
    NodeRunner,
)
from common.audit import FaultyNodeAutidior


CONSENSUS_MODULE = get_fba_module('isaac')


parser = ArgumentParserShowDefaults()
logger.set_argparse(parser)
parser.add_argument(
    'case',
    help='set the case name',
    type=str,
)

parser.add_argument(
    'design',
    help='design yaml',
    type=str,
)


def run(options, design):
    blockchains = list()
    for node_design in design.nodes:
        consensus = CONSENSUS_MODULE.Consensus(
            node_design.node,
            node_design.quorum.threshold,
            node_design.quorum.validators,
        )

        faulties = getattr(design.faulties, node_design.node.name, list())
        if len(faulties) > 0:
            blockchain = FaultyBlockchain(faulties, consensus)
        else:
            blockchain = Blockchain(consensus)

        blockchains.append(blockchain)

        NodeRunner(blockchain).start()
        FaultyNodeAutidior(blockchain).start()

    return blockchains


if __name__ == '__main__':
    options = parser.parse_args()

    logger.from_argparse(logger, options)
    logger.set_level(logging.FATAL, 'http')
    logger.set_level(logging.FATAL, 'transport')

    design = load_design(options.design)

    log = logger.get_logger(__name__)
    log_state = logger.get_logger('consensus.state')

    log.info('design loaded:\n%s', pprint.pformat(convert_namedtuple_to_dict(design), width=1))

    log.debug('trying to run %d / %d (faulty nodes / all nodes)', len(design.faulties), len(design.nodes))

    try:
        os.chdir(pathlib.Path(options.case).absolute())
        sys.path.insert(0, '.')

        run_func = getattr(get_module('main'), 'run', None)
    except FileNotFoundError:
        run_func = None

    if run_func is None:
        log.debug('failed to load case, %s', options.case)

        run_func = run

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
