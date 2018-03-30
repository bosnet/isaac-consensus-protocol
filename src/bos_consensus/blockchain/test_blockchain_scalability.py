import copy

from bos_consensus.common import Ballot, BallotVotingResult, Message, node_factory
from bos_consensus.blockchain import Blockchain
from bos_consensus.network import Endpoint
from bos_consensus.consensus import get_fba_module
from bos_consensus.consensus.fba.isaac import IsaacState
from bos_consensus.blockchain.util import StubTransport

IsaacConsensus = get_fba_module('isaac').IsaacConsensus


def receive_copy_ballot(self, ballot):
    new_ballot = copy.deepcopy(ballot)
    self.consensus.handle_ballot(new_ballot)


def check_slot_time_stub(ballot):
    pass


def blockchain_factory(name, address, threshold, validator_endpoint_uris, slot_size):
    node = node_factory(name, Endpoint.from_uri(address))
    validators = list()
    for uri in validator_endpoint_uris:
        validators.append(
            node_factory(uri, Endpoint.from_uri(uri)),
        )

    consensus = IsaacConsensus(node, threshold, validators, slot_size)
    consensus._check_slot_time = check_slot_time_stub
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
        ballots.append(Ballot(ballot.ballot_id, node_names[i], message, IsaacState.INIT, BallotVotingResult.agree,
                              ballot.timestamp))

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
            threshold,
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


def run_blockchain_scalability(n_nodes, threshold, n_ballots_in_slot, n_sending_ballots):
    assert n_nodes > 1

    node_names = generate_node_names('http://localhost:', n_nodes)
    blockchains = generate_blockchains(node_names, threshold, n_ballots_in_slot)
    set_validator_all_each_other(blockchains)
    ballots_list = generate_n_ballots_list(node_names, n_sending_ballots)
    assert ballots_list

    ballot_size = len(ballots_list[0])

    # receive multiple ballots simultaniously
    for i in range(ballot_size):
        for ballots in ballots_list:
            for blockchain in blockchains:
                blockchain.receive_ballot(ballots[i])

    for blockchain in blockchains:
        check_all_ballot_state_in_slot(blockchain.consensus.slot, ballots_list, IsaacState.SIGN)

    set_all_ballots_state_to(ballots_list, IsaacState.SIGN)

    # receive multiple ballots simultaniously
    for i in range(ballot_size):
        for ballots in ballots_list:
            for blockchain in blockchains:
                blockchain.receive_ballot(ballots[i])

    for blockchain in blockchains:
        check_all_ballot_state_in_slot(blockchain.consensus.slot, ballots_list, IsaacState.ACCEPT)

    set_all_ballots_state_to(ballots_list, IsaacState.ACCEPT)

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


def test_blockchain_scalability():
    run_blockchain_scalability(3, 100, 2, 2)
    run_blockchain_scalability(5, 100, 10, 10)

    return
