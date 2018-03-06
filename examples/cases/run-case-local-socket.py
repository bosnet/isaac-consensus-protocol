import asyncio
import logging
import os
import pathlib
import pprint  # noqa
import sys  # noqa

from bos_consensus.common import Message
from bos_consensus.blockchain import Blockchain
from bos_consensus.consensus import get_fba_module
from bos_consensus.network import get_network_module
from bos_consensus.util import (
    ArgumentParserShowDefaults,
    convert_namedtuple_to_dict,
    get_module,
    logger,
)

from common import (
    FaultyBlockchain,
    load_design,
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
    help='design yaml',
    type=str,
)

MS = 0.001


async def send_message_coroutine(local_server, node_info, message_infos):
    for message_info in message_infos:
        message_str = message_info[0]
        interval = message_info[1]
        message = Message.new(message_str)
        endpoint = node_info.endpoint
        log.debug(f'send message to {endpoint}')
        local_server.blockchain.transport.send(endpoint, message.serialize())
        await asyncio.sleep(interval * MS)


async def log_nodes_state(blockchains, design, log_state):
    prev = None
    while True:
        await asyncio.sleep(1)

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

    return


def set_message_task(loop, design, nodes, local_server):
    if 'messages' in design._fields:
        for node_name, message in design.messages._asdict().items():
            message_infos = []
            for i in range(message.number):
                new_message = message.message_format % i
                message_infos.append((new_message, message.interval))
            node_info = nodes[node_name]
            loop.create_task(send_message_coroutine(local_server, node_info, message_infos))


def run(options, design):
    log_state = logger.get_logger('consensus.state')

    network_module = get_network_module('local_socket')

    blockchains = list()
    loop = asyncio.get_event_loop()
    nodes = dict()
    servers = dict()
    auditors = dict()
    for node_design in design.nodes:
        node = node_design.node
        nodes[node.name] = node
        consensus = CONSENSUS_MODULE.Consensus(
            node,
            node_design.quorum.threshold,
            node_design.quorum.validators,
        )

        for validator in node_design.quorum.validators:
            consensus.add_to_validator_connected(validator)

        transport = network_module.Transport(node, loop)
        faulties = getattr(design.faulties, node.name, list())
        if len(faulties) > 0:
            blockchain = FaultyBlockchain(faulties, consensus, transport)
        else:
            blockchain = Blockchain(consensus, transport)

        blockchains.append(blockchain)
        servers[node.name] = network_module.Server(blockchain)
        auditors[node.name] = FaultyNodeAuditor(blockchain, loop, 1)

    for server in servers.values():
        server.start()

    [asyncio.ensure_future(auditor.start()) for auditor in auditors.values()]

    try:
        local_server = list(servers.values())[0]
        set_message_task(loop, design, nodes, local_server)
        loop.create_task(log_nodes_state(blockchains, design, log_state))
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        log.debug('exception occured!')
    finally:
        pass

    return


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

    run_func(options, design)
