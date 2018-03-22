import copy
import time

from bos_consensus.common import Ballot, BallotVotingResult, Message, node_factory
from bos_consensus.blockchain import Blockchain
from bos_consensus.network import Endpoint
from bos_consensus.consensus import get_fba_module
from bos_consensus.consensus.fba.isaac import IsaacState
from bos_consensus.blockchain.util import StubTransport

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
log = None

IsaacConsensus = get_fba_module('isaac').IsaacConsensus


def receive_copy_ballot(self, ballot):
    new_ballot = copy.deepcopy(ballot)
    self.consensus.handle_ballot(new_ballot)


def blockchain_factory(name, address, threshold, validator_endpoint_uris, slot_size=5):
    node = node_factory(name, Endpoint.from_uri(address))
    validators = list()
    for uri in validator_endpoint_uris:
        validators.append(
            node_factory(uri, Endpoint.from_uri(uri)),
        )

    consensus = IsaacConsensus(node, threshold, validators, slot_size)
    Blockchain.receive_ballot = receive_copy_ballot
    return Blockchain(
        consensus,
        StubTransport()
    )


def generate_ballots(node_names):
    message = Message.new()
    ballots = list()
    n_node = len(node_names)
    assert n_node > 1
    ballot = Ballot.new(node_names[0], message, IsaacState.INIT, BallotVotingResult.agree)
    ballots.append(ballot)
    for i in range(1, n_node):
        ballots.append(Ballot(ballot.ballot_id, node_names[i], message, IsaacState.INIT, BallotVotingResult.agree, ballot.timestamp))

    return ballots


def generate_n_ballots_list(node_names, n):
    ballots_list = list()

    for _ in range(n):
        ballots_list.append(generate_ballots(node_names))

    return ballots_list


def check_all_ballot_state_in_slot(slot, ballots_list, state):
    for ballots in ballots_list:
        assert ballots
        assert slot.get_ballot_state(ballots[0]) == state

    return


def set_all_ballots_state_to(ballots_list, state):
    for ballots in ballots_list:
        for ballot in ballots:
            ballot.state = state

    return


def get_messages_from_ballots_list(ballots_list):
    messages = list()
    for ballots in ballots_list:
        if ballots:
            messages.append(ballots[0].message)

    return messages


def generate_node_names(node_name_prefix, n):
    INIT = 5000
    node_names = list()
    for i in range(1, n+1):
        node_names.append(f'http://localhost:{INIT+i}')

    return node_names


def generate_blockchains(node_names, threshold, slot_size=5):
    blockchains = list()
    for i in range(len(node_names)):
        validators = copy.deepcopy(node_names)
        node_name = node_names[i]
        validators.remove(node_name)
        blockchain = blockchain_factory(
            node_name,
            node_name,
            100,
            validators,
            slot_size,
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


def test_performance_init_to_all_confirm_sequence(n_nodes, threshold, n_ballots_in_slot, n_sending_ballots):
    assert n_nodes > 1

    log.fatal('1. Generate_node_names')
    log.metric(
        action='performance-test',
        kind='generate node names',
        timing='begin',
    )
    start = time.time()
    node_names = generate_node_names('http://localhost:', n_nodes)
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
    blockchains = generate_blockchains(node_names, threshold, n_ballots_in_slot)
    # validator configuration
    set_validator_all_each_other(blockchains)
    end = time.time()
    log.fatal(f'   Generate_blockchains elapsed time={end - start:.3} sec')
    log.metric(
        action='performance-test',
        kind=f'generate blockchains',
        timing='end',
        elapsed_time=f'{end-start:.3} sec',
    )

    log.fatal('3. generate_n_ballots_list')
    log.metric(
        action='performance-test',
        kind='generate n ballot list',
        timing='begin',
    )
    start = time.time()
    ballots_list = generate_n_ballots_list(node_names, n_sending_ballots)
    end = time.time()
    log.fatal(f'   Generate_n_ballots_list elapsed time={end - start:.3} sec')

    log.metric(
        action='performance-test',
        kind=f'generate n ballot list',
        timing='end',
        elapsed_time=f'{end-start:.3} sec',
    )

    assert ballots_list

    ballot_size = len(ballots_list[0])

    log.fatal('4. receive INIT state ballots and check state SIGN')
    log.metric(
        action='performance-test',
        kind='receive INIT state and check state SIGN',
        timing='begin',
    )
    start = time.time()

    # receive multiple ballots simultaniously
    for i in range(ballot_size):
        for ballots in ballots_list:
            for blockchain in blockchains:
                blockchain.receive_ballot(ballots[i])

    for blockchain in blockchains:
        check_all_ballot_state_in_slot(blockchain.consensus.slot, ballots_list, IsaacState.SIGN)
    end = time.time()
    log.fatal(f'   Receive INIT state ballots and check state SIGN elapsed time={end - start:.3} sec')

    log.metric(
        action='performance-test',
        kind=f'receive INIT state and check state SIGN',
        timing='end',
        elapsed_time=f'{end-start:.3} sec',
    )

    log.fatal('5. receive SIGN state ballots and check state ACCEPT')
    log.metric(
        action='performance-test',
        kind='receive SIGN state and check state ACCEPT',
        timing='begin',
    )

    start = time.time()

    set_all_ballots_state_to(ballots_list, IsaacState.SIGN)

    # receive multiple ballots simultaniously
    for i in range(ballot_size):
        for ballots in ballots_list:
            for blockchain in blockchains:
                blockchain.receive_ballot(ballots[i])

    for blockchain in blockchains:
        check_all_ballot_state_in_slot(blockchain.consensus.slot, ballots_list, IsaacState.ACCEPT)

    end = time.time()
    log.fatal(f'   Receive SIGN state ballots and check state ACCEPT elapsed time={end - start:.3} sec')

    log.metric(
        action='performance-test',
        kind=f'receive SIGN state and check state ACCEPT',
        timing='end',
        elapsed_time=f'{end-start:.3} sec',
    )

    set_all_ballots_state_to(ballots_list, IsaacState.ACCEPT)

    log.fatal('6. receive ACCEPT ballots and check state ALL_CONFIRM')
    log.metric(
        action='performance-test',
        kind='receive ACCEPT ballots and check state ALL_CONFIRM',
        timing='begin',
    )
    start = time.time()

    # receive multiple ballots simultaniously
    for i in range(ballot_size):
        for ballots in ballots_list:
            for blockchain in blockchains:
                blockchain.receive_ballot(ballots[i])

    messages = get_messages_from_ballots_list(ballots_list)

    # check all confirm by save message
    for message in messages:
        for blockchain in blockchains:
            assert message in blockchain.consensus.messages

    end = time.time()
    log.fatal(f'   Receive ACCEPT state ballots and check state ALL_CONFIRM elapsed time={end - start:.3} sec')

    log.metric(
        action='performance-test',
        kind=f'receive ACCEPT ballots and check state ALL_CONFIRM',
        timing='end',
        elapsed_time=f'{end-start:.3} sec',
    )


def main(options):
    nodes = options.nodes
    threshold = options.threshold
    ballots = options.ballots
    sending = options.sending

    log.fatal(f'Number of nodes={nodes}')
    log.fatal(f'Threshold={threshold}')
    log.fatal(f'Number of ballots in slot={ballots}')
    log.fatal(f'Number of sending ballots={sending}')

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
    test_performance_init_to_all_confirm_sequence(nodes, threshold, ballots, sending)
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
