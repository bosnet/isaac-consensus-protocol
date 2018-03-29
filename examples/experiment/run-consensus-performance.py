import asyncio
import copy
import time

from bos_consensus.common import Message, node_factory
from bos_consensus.blockchain import Blockchain
from bos_consensus.network import Endpoint, get_network_module
from bos_consensus.consensus import get_fba_module

from bos_consensus.util import (
    logger,
    ArgumentParserShowDefaults,
)

parser = ArgumentParserShowDefaults()
logger.set_argparse(parser)
parser.add_argument(
    '-n',
    '--nodes',
    help='Number of nodes',
    default=5,
    type=int
)
parser.add_argument(
    '-t',
    '--threshold',
    help='Threshold of all nodes',
    default=60,
    type=int
)
parser.add_argument(
    '-b',
    '--ballots',
    help='Number of ballots in slot',
    default=5,
    type=int
)
parser.add_argument(
    '-s',
    '--sending',
    help='Number of sending ballots simultaniously',
    default=5,
    type=int
)
parser.add_argument(
    '-cp',
    '--consensus_protocol',
    help='ex. isaac, instantsend',
    default='isaac',
    type=str
)
log = None

Consensus = None
network_module = get_network_module('local_socket')
loop = asyncio.get_event_loop()


def blockchain_factory(Consensus, name, address, threshold, validators, slot_size, queue_size):
    node = node_factory(name, Endpoint.from_uri(address))
    consensus = Consensus(node, threshold, validators, slot_size)
    transport = network_module.Transport(node, loop)

    return Blockchain(
        consensus,
        transport
    )


def generate_n_messages(message_count):
    messages = list()

    for _ in range(message_count):
        messages.append(Message.new())

    return messages


def generate_node_names(node_name_prefix, n):
    INIT = 5000
    node_names = list()
    node_endpoints = list()
    for i in range(1, n+1):
        node_names.append(f'n{i}')
        node_endpoints.append(f'{node_name_prefix}:{INIT+i}')

    return node_names, node_endpoints


def generate_blockchains(Consensus, node_names, node_endpoints, threshold, slot_size=5, queue_size=100):
    blockchains = list()
    nodes = list()
    for i in range(len(node_names)):
        nodes.append(node_factory(node_names[i], Endpoint.from_uri(node_endpoints[i])))

    for i in range(len(node_names)):
        validators = copy.deepcopy(nodes)
        del validators[i]
        blockchain = blockchain_factory(
            Consensus,
            node_names[i],
            node_endpoints[i],
            100,
            validators,
            slot_size,
            queue_size
        )
        blockchains.append(blockchain)

    return blockchains


def get_validator_nodes(blockchains, blockchain):
    nodes = [blockchain.node for blockchain in blockchains]
    nodes.remove(blockchain.node)
    return nodes


def set_validator_all_each_other(blockchains):
    for blockchain in blockchains:
        validator_nodes = get_validator_nodes(blockchains, blockchain)
        for node in validator_nodes:
            blockchain.consensus.add_to_validator_connected(node)
        blockchain.consensus.init()


async def send_bulk_message(messages, endpoint, local_server):
    assert type(messages) in (list, tuple,)
    for message in messages:
        local_server.blockchain.transport.send(endpoint, message.serialize())
        await asyncio.sleep(0.001)

    await asyncio.sleep(0.1)

    return


def test_performance_init_to_all_confirm_sequence(Consensus, n_nodes, threshold, n_ballots_in_slot, n_sending_messages):
    assert n_nodes > 1

    log.fatal('1. Generate_node_names')
    log.metric(
        action='performance-test',
        kind='generate node names',
        timing='begin',
    )
    start = time.time()
    node_names, node_endpoints = generate_node_names('http://127.0.0.1', n_nodes)
    end = time.time()
    log.fatal(f'   Generate_node_names elapsed time={end - start:.3} sec')
    log.metric(
        action='performance-test',
        kind=f'generate node names',
        timing='end',
        elapsed_time=f'{end-start:.3} sec',
    )

    log.fatal('2. generate_blockchains')
    log.metric(
        action='performance-test',
        kind='generate blockchains',
        timing='begin',
    )
    start = time.time()
    blockchains = generate_blockchains(Consensus, node_names, node_endpoints, threshold, n_ballots_in_slot)
    assert len(blockchains) > 0
    set_validator_all_each_other(blockchains)

    servers = dict()

    for blockchain in blockchains:
        servers[blockchain.node.name] = network_module.Server(blockchain)

    for server in servers.values():
        server.start()

    end = time.time()
    log.fatal(f'   Generate_blockchains elapsed time={end - start:.3} sec')
    log.metric(
        action='performance-test',
        kind=f'generate blockchains',
        timing='end',
        elapsed_time=f'{end-start:.3} sec',
    )

    log.fatal('3. generate_n_messages')
    log.metric(
        action='performance-test',
        kind='generate n messages',
        timing='begin',
    )
    start = time.time()
    messages = generate_n_messages(n_sending_messages)
    end = time.time()
    log.fatal(f'   Generate_n_messages elapsed time={end - start:.3} sec')

    log.metric(
        action='performance-test',
        kind=f'generate n messages',
        timing='end',
        elapsed_time=f'{end-start:.3} sec',
    )

    log.fatal(f'4. send message and run consensus')
    log.metric(
        action='performance-test',
        kind=f'send message and run consensus',
        timing='begin',
    )
    start = time.time()

    try:
        loop.run_until_complete(send_bulk_message(messages, blockchains[1].node.endpoint, list(servers.values())[0]))
    except (KeyboardInterrupt, SystemExit):
        log.debug('exception occured!')
    finally:
        loop.close()

    end = time.time()
    log.fatal(f'   send message and run consensus elapsed time={end - start:.3} sec')

    log.metric(
        action='performance-test',
        kind=f'send message and run consensus',
        timing='end',
        elapsed_time=f'{end-start:.3} sec',
    )

    for message in messages:
        for blockchain in blockchains:
            assert message in blockchain.consensus.messages


def main(options):
    nodes = options.nodes
    threshold = options.threshold
    ballots = options.ballots
    sending = options.sending
    consensus_protocol = options.consensus_protocol

    log.fatal(f'Number of nodes={nodes}')
    log.fatal(f'Threshold={threshold}')
    log.fatal(f'Number of ballots in slot={ballots}')
    log.fatal(f'Number of sending ballots={sending}')
    assert consensus_protocol in ('isaac', 'instantsend',)
    log.fatal(f'Consensus protocol={consensus_protocol}')

    log.metric(
        action='performance-test',
        kind=f'whole process',
        timing='begin',
        nodes=nodes,
        Threshold=threshold,
        ballots=ballots,
        sending=sending,
        )

    start = time.time()

    Consensus = get_fba_module(consensus_protocol).Consensus
    test_performance_init_to_all_confirm_sequence(Consensus, nodes, threshold, ballots, sending)
    end = time.time()
    log.fatal(f'Total Elapsed time={end - start:.3} sec')

    log.metric(
        action='performance-test',
        kind=f'whole process',
        timing='end',
        elapsed_time=f'{end-start:.3} sec',
    )


if __name__ == '__main__':
    options = parser.parse_args()
    logger.from_argparse(logger, options)

    log = logger.get_logger(__name__)

    log.debug('options: %s', options)
    log.debug('log settings: %s', logger.info)

    main(options)
