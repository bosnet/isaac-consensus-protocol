import asyncio
import graphviz
import logging
import os
import pathlib
import pprint  # noqa
import sys  # noqa
import time

from common import (
    FaultyBlockchain,
    load_design,
    NodeRunner,
)
from common.audit import FaultyNodeAuditor

from bos_consensus.blockchain import Blockchain
from bos_consensus.consensus import get_fba_module
from bos_consensus.network import get_network_module
from bos_consensus.util import (
    ArgumentParserShowDefaults,
    convert_namedtuple_to_dict,
    get_module,
    logger,
    Printer,
)
from util import log_current_state

CONSENSUS_MODULE = get_fba_module('isaac')

PRINTER = Printer(sys.stdout)

parser = ArgumentParserShowDefaults()
logger.set_argparse(parser)

parser.add_argument(
    '-case',
    help='set the case name',
    default=None,
    type=str,
)

parser.add_argument(
    '-viz-format',
    default='png',
    help='network topology image format',
    type=str,
    choices=graphviz.FORMATS,
)
parser.add_argument('-viz-dpi', help='network topology image dpi', type=int, default=300)
parser.add_argument('-viz-output', help='network topology image output file', type=str)

parser.add_argument(
    'design',
    help='design should be yaml or json',
    type=str,
)


parser.add_argument(
    'action',
    nargs='?',
    default='run',
    help='action',
    choices=('run', 'check'),
    type=str,
)


def run_default(options, design):
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

    coroutines = list()
    for auditor in auditors.values():
        coroutines.extend(auditor.get_coroutines())

    try:
        loop.run_until_complete(asyncio.gather(asyncio.gather(*tuple(coroutines))))
    except (KeyboardInterrupt, SystemExit):
        log.debug('exception occured!')

    return blockchains


def run(options, design):
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

    run_func = run_default
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

        now = set(map(lambda x: (x.consensus.node.name, x.consensus), blockchains))
        if now == prev:
            continue

        prev = now
        log_current_state(now, design, log_state)

    return


def _check_consensus_is_possible(validators, disabled_nodes):
    return len(validators) >= (3 * len(disabled_nodes) + 1)


def check(options, design):
    validators_by_node = dict()
    faulty_nodes = set()

    for node_design in design.nodes:
        node_name = node_design.node.name
        faulties = getattr(design.faulties, node_name, list())
        if len(faulties) > 0:
            faulty_nodes.add(node_name)

        validators = set(map(lambda x: x.name, node_design.quorum.validators))
        validators.add(node_name)
        validators_by_node[node_name] = validators
        log.debug('node, %s has the validators: %s', node_name, validators)

    # check whether each node can reach consensus
    # 1. trying to find 'nonconsensus' nodes
    nonconsensus_nodes = faulty_nodes.copy()
    while True:
        current_nonconsensus_nodes = nonconsensus_nodes.copy()
        for node_design in design.nodes:
            node_name = node_design.node.name
            if node_name in current_nonconsensus_nodes:
                continue

            if node_name in faulty_nodes:
                continue

            validators = validators_by_node[node_name]
            faulties = validators & faulty_nodes
            nonconsensus_nodes_in_node = validators & nonconsensus_nodes

            if len(nonconsensus_nodes_in_node) < 1:
                continue

            # this node can reach the consensus
            can_pass = _check_consensus_is_possible(validators, faulties | nonconsensus_nodes_in_node)
            if not can_pass and node_name not in current_nonconsensus_nodes:
                current_nonconsensus_nodes.add(node_name)
                log.debug(
                    'found nonconsesus node: node=%s found nonconsensus-nodes=%s',
                    node_name,
                    nonconsensus_nodes,
                )

        if nonconsensus_nodes == current_nonconsensus_nodes:
            break

        nonconsensus_nodes = current_nonconsensus_nodes

    log.debug('found all the nonconsensus node: %s', sorted(nonconsensus_nodes))

    # 3. check again whether each node can reach the consensus
    for node_design in design.nodes:
        node_name = node_design.node.name

        validators = validators_by_node[node_name]
        disabled_nodes = validators & nonconsensus_nodes

        PRINTER.head(node_name)
        PRINTER.line('=')
        PRINTER.format('validators', ', '.join(sorted(validators)), fmt='%15s | %s', print=True)
        PRINTER.line()
        if len(disabled_nodes) > 0:
            disabled_nodes_string = ', '.join(sorted(disabled_nodes))
        else:
            disabled_nodes_string = '-'
        PRINTER.format('disabled nodes', disabled_nodes_string, fmt='%15s | %s', print=True)
        PRINTER.line()

        can_pass = _check_consensus_is_possible(validators, disabled_nodes)
        PRINTER.format(
            'can consensus?',
            PRINTER.colored('Yes' if can_pass else 'No', color='green' if can_pass else 'red'),
            fmt='%15s | %s',
            print=True,
        )
        PRINTER.line('=')
        PRINTER.print()

    return


def vizualize_quorums(options, design):
    quorums = dict()
    for node_design in design.nodes:
        node = node_design.node

        quorums[node.name] = [node.name]
        for validator in node_design.quorum.validators:
            quorums[node.name].append(validator.name)

    g = graphviz.Digraph('G', format=options.viz_format, engine='fdp')
    g.graph_attr.update(
        fontname='monospace',
        size='100,100',
        dpi=str(options.viz_dpi),
        fontsize='10',
        style='rounded',
        splines='curved',
    )
    g.edge_attr.update(
        fontname='monospace', fontsize='6', penwidth='0.5', arrowsize='0.5', arrowhead=None, color='gray',
    )
    g.node_attr.update(
        fontname='monospace',
        fontsize='10',
        style='filled',
        color='snow',
        fontcolor='snow',
        fillcolor='crimson',
        shape='circle',
        penwidth='0'
    )

    line_connected = dict()

    for node, validators in quorums.items():
        for validator in validators:
            if node == validator:
                continue

            arrowhead = 'normal'
            arrowtail = 'normal'
            unary = False

            if node not in quorums[validator]:
                arrowtail = 'dot'
                unary = True

            key = tuple(sorted([node, validator]))
            if key in line_connected:
                continue

            line_connected[key] = True
            g.edge(
                node,
                validator,
                arrowsize='0.3',
                arrowhead=arrowhead,
                arrowtail=arrowtail,
                color='gray79' if unary else 'gray31',
                dir='both',
                fontcolor='gray79' if unary else 'gray31',
                penwidth='1',
            )

    if options.viz_output.split('.')[-1].lower() == options.viz_format:
        options.viz_output = options.viz_output[:-1 * (len(options.viz_format) + 1)]

    g.render(options.viz_output, cleanup=True)

    return


if __name__ == '__main__':
    options = parser.parse_args()

    logger.from_argparse(logger, options)
    logger.set_level(logging.FATAL, 'http')
    logger.set_level(logging.FATAL, 'transport')

    if not pathlib.Path(options.design).exists():
        parser.error('file, `%s` does not exists.' % options.design)

    if not pathlib.Path(options.design).is_file():
        parser.error('file, `%s` is not valid file.' % options.design)

    design = load_design(options.design)

    log = logger.get_logger(__name__)
    log_state = logger.get_logger('consensus.state')

    log.debug('options: %s', options)

    log.info('design loaded:\n%s', pprint.pformat(convert_namedtuple_to_dict(design), width=1))

    if options.viz_output is not None:
        vizualize_quorums(options, design)
    elif options.action in ('run',):
        run(options, design)
    elif options.action in ('check',):
        check(options, design)

    sys.exit(0)
