import copy

from bos_consensus.common import Ballot, BallotVotingResult, Message, node_factory
from bos_consensus.consensus import get_fba_module
from bos_consensus.network import Endpoint
from .blockchain import Blockchain
from .util import StubTransport


def copy_ballot(ballot, node_name, state):
    new_ballot = copy.copy(ballot)
    new_ballot.node_name = node_name
    new_ballot.timestamp = ballot.timestamp
    if state is not None:
        new_ballot.state = state

    return new_ballot


Consensus = get_fba_module('isaac').Consensus
IsaacState = get_fba_module('isaac').State


class SimpleBlockchain(Blockchain):
    def __init__(self, *a, **kw):
        super(SimpleBlockchain, self).__init__(*a, **kw)

    def receive_ballots(self, *ballots):
        for ballot in ballots:
            self.receive_ballot(ballot)

        return


def simple_blockchain_factory(name, address, threshold, validator_endpoint_uris):
    node = node_factory(name, Endpoint.from_uri(address))

    validators = list()
    for uri in validator_endpoint_uris:
        validators.append(
            node_factory(uri, Endpoint(uri, uri, 0)),
        )

    consensus = Consensus(node, threshold, validators)

    transport = StubTransport(bind=('0.0.0.0', 5001))

    return SimpleBlockchain(consensus, transport)


def test_same_message_after_allconfirm():
    node_id_1 = 'n1'
    node_id_2 = 'n2'
    node_id_3 = 'n3'

    blockchain1 = simple_blockchain_factory(
        node_id_1,
        'http://localhost:5001',
        100,
        [node_id_2, node_id_3],
    )

    node2 = node_factory(node_id_2, Endpoint.from_uri('http://localhost:5002'))
    node3 = node_factory(node_id_3, Endpoint.from_uri('http://localhost:5003'))

    blockchain1.consensus.add_to_validator_connected(node2)
    blockchain1.consensus.add_to_validator_connected(node3)

    message = Message.new('message')

    ballot1 = Ballot.new(node_id_1, message, IsaacState.INIT, BallotVotingResult.agree)
    ballot2 = copy_ballot(ballot1, node_id_2, IsaacState.INIT)
    ballot3 = copy_ballot(ballot1, node_id_3, IsaacState.INIT)

    blockchain1.receive_ballots(ballot1, ballot2, ballot3)

    assert blockchain1.consensus.slot.get_ballot_state(ballot1) == IsaacState.SIGN

    ballot1 = copy_ballot(ballot1, node_id_1, IsaacState.SIGN)
    ballot2 = copy_ballot(ballot1, node_id_2, IsaacState.SIGN)
    ballot3 = copy_ballot(ballot1, node_id_3, IsaacState.SIGN)

    blockchain1.receive_ballots(ballot1, ballot2, ballot3)

    assert blockchain1.consensus.slot.get_ballot_state(ballot1) == IsaacState.ACCEPT

    ballot1 = copy_ballot(ballot1, node_id_1, IsaacState.ACCEPT)
    ballot2 = copy_ballot(ballot1, node_id_2, IsaacState.ACCEPT)
    ballot3 = copy_ballot(ballot1, node_id_3, IsaacState.ACCEPT)

    blockchain1.receive_ballots(ballot1, ballot2, ballot3)

    assert message in blockchain1.consensus.messages

    # send same message in new ballot
    new_ballot1 = Ballot.new(node_id_1, message, IsaacState.INIT, BallotVotingResult.agree)

    assert new_ballot1.ballot_id != ballot1.ballot_id

    ballot1 = copy_ballot(new_ballot1, node_id_1, IsaacState.INIT)
    ballot2 = copy_ballot(new_ballot1, node_id_2, IsaacState.INIT)
    ballot3 = copy_ballot(new_ballot1, node_id_3, IsaacState.INIT)

    blockchain1.receive_ballots(ballot1, ballot2, ballot3)

    # node state still remains the previous state
    assert message in blockchain1.consensus.messages
    ballots = blockchain1.consensus.slot.get_validator_ballots(new_ballot1).values()
    assert not ballots

    return


def test_same_message_after_init():
    node_id_1 = 'n1'
    node_id_2 = 'n2'
    node_id_3 = 'n3'

    blockchain1 = simple_blockchain_factory(
        node_id_1,
        'http://localhost:5001',
        100,
        [node_id_2, node_id_3],
    )

    node2 = node_factory(node_id_2, Endpoint.from_uri('http://localhost:5002'))
    node3 = node_factory(node_id_3, Endpoint.from_uri('http://localhost:5003'))

    blockchain1.consensus.add_to_validator_connected(node2)
    blockchain1.consensus.add_to_validator_connected(node3)

    message = Message.new('message')

    ballot1 = Ballot.new(node_id_1, message, IsaacState.INIT, BallotVotingResult.agree)
    ballot2 = copy_ballot(ballot1, node_id_2, IsaacState.INIT)
    ballot3 = copy_ballot(ballot1, node_id_3, IsaacState.INIT)

    blockchain1.receive_ballots(ballot1, ballot2, ballot3)

    assert blockchain1.consensus.slot.get_ballot_state(ballot1) == IsaacState.SIGN

    existing_ballot_ids = set(map(lambda x: x.ballot_id, filter(lambda x: x is not None, blockchain1.consensus.slot.get_all_ballots())))

    # send same message in new ballot, which has previous state
    new_ballot1 = Ballot.new(node_id_1, message, IsaacState.INIT, BallotVotingResult.agree)

    assert new_ballot1.ballot_id != ballot1.ballot_id

    ballot1 = copy_ballot(new_ballot1, node_id_1, IsaacState.INIT)
    ballot2 = copy_ballot(new_ballot1, node_id_2, IsaacState.INIT)
    ballot3 = copy_ballot(new_ballot1, node_id_3, IsaacState.INIT)

    blockchain1.receive_ballots(ballot1, ballot2, ballot3)

    # node doesn't have ballot1, so ballot1 in node state is NONE
    assert blockchain1.consensus.slot.get_ballot_state(ballot1) == IsaacState.NONE
    list(filter(
        lambda x: x.ballot_id == ballot1.ballot_id, blockchain1.consensus.slot.get_validator_ballots(ballot1).values()
    ))
    assert len([]) < 1

    current_ballot_ids = set(map(lambda x: x.ballot_id, filter(lambda x: x is not None, blockchain1.consensus.slot.get_all_ballots())))

    assert existing_ballot_ids == current_ballot_ids

    return
