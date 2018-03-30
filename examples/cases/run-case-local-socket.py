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
from util import log_current_state

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
    help='design should be yaml or json',
    type=str,
)

MS = 0.001


def run(options, design):
    log_state = logger.get_logger('consensus.state')

    network_module = get_network_module('local_socket')

    loop = asyncio.get_event_loop()

    blockchains = list()
    nodes = dict()
    servers = dict()
    auditors = dict()

    audit_waiting = design.common.audit_waiting
    audit_time_limit = design.common.audit_time_limit

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
        auditors[node.name] = FaultyNodeAuditor(blockchain, loop, audit_waiting, audit_time_limit)

    for server in servers.values():
        server.start()

    try:
        coros = list()
        for auditor in auditors.values():
            coros.extend(auditor.get_coroutines())
        loop.run_until_complete(asyncio.gather(
            asyncio.gather(*tuple(coros)),
            send_bulk_message_coro(design, nodes, list(servers.values())[0]),
        ))
    except (KeyboardInterrupt, SystemExit):
        log.debug('exception occured!')
    finally:
        loop.close()

    log_nodes_state(blockchains, design, log_state)
    check_safety(blockchains)

    return


def check_safety(blockchains):
    safety_result = dict()
    for blockchain in blockchains:
        if isinstance(blockchain, FaultyBlockchain):
            continue
        messages_hash = hash(blockchain.consensus)
        if messages_hash not in safety_result:
            safety_result[messages_hash] = list()
        if messages_hash in safety_result:
            safety_result[messages_hash].append(blockchain)

    if len(safety_result) == 1:
        blockchain = list(safety_result.values())[0][0]
        if len(blockchain.consensus.messages) > 0:
            log_state.metric(
                action='safety_check',
                result='success',
            )
        else:
            log_state.metric(
                action='safety_check',
                result='fail',
                info='empty messages'
            )
    else:
        result_list = list()
        for messages_hash, blockchains in safety_result.items():
            result_dict = dict()
            result_dict['message_hash'] = messages_hash
            result_dict['nodes'] = [b.consensus.node_name for b in blockchains]
            result_dict['messages'] = list() if not blockchains else blockchains[0].consensus.messages
            result_list.append(result_dict)

        log_state.metric(
            action='safety_check',
            result='fail',
            info=result_list
        )

    if len(safety_result) == 1:
        log_state.info('[SAFETY] OK!')
    else:
        log_state.info('[SAFETY] FAIL!')

    return


async def send_bulk_message_coro(design, nodes, local_server):
    if 'messages' in design._fields:
        for node_name, message in design.messages._asdict().items():
            message_infos = []
            for _ in range(message.number):
                new_message = Message.new()
                message_infos.append((new_message, message.interval))
            node_info = nodes[node_name]
            await send_message_coroutine(local_server, node_info, message_infos)

    return


async def send_message_coroutine(local_server, node_info, message_infos):
    for message_info in message_infos:
        message = message_info[0]
        interval = message_info[1]
        endpoint = node_info.endpoint
        log.debug(f'send message to {endpoint}')
        local_server.blockchain.transport.send(endpoint, message.serialize())
        await asyncio.sleep(interval * MS)

    return


def log_nodes_state(blockchains, design, log_state):
    now = set(map(lambda x: (x.consensus.node.name, x.consensus), blockchains))
    log_current_state(now, design, log_state)

    return


if __name__ == '__main__':
    options = parser.parse_args()

    logger.from_argparse(logger, options)
    logger.set_level(logging.FATAL, 'local')
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
