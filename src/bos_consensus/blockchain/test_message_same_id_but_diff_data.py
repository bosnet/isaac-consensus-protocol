import copy

from ..common import Ballot, Message, node_factory, BallotVotingResult
from ..network import Endpoint
from ..blockchain import Blockchain
from ..consensus import get_fba_module
from ..consensus.fba.isaac import IsaacState
from .util import StubTransport


IsaacConsensus = get_fba_module('isaac').IsaacConsensus


def receive_copy_ballot(self, ballot):
    new_ballot = copy.deepcopy(ballot)
    self.consensus.handle_ballot(new_ballot)


def blockchain_factory(name, address, threshold, validator_endpoint_uris):
    node = node_factory(name, Endpoint.from_uri(address))
    validators = list()
    for uri in validator_endpoint_uris:
        validators.append(
            node_factory(uri, Endpoint.from_uri(uri)),
        )

    consensus = IsaacConsensus(node, threshold, validators)
    Blockchain.receive_ballot = receive_copy_ballot
    return Blockchain(
        consensus,
        StubTransport()
    )


def test_state_init_to_all_confirm_diff_message_data():
    node_name_1 = 'http://localhost:5001'
    node_name_2 = 'http://localhost:5002'
    node_name_3 = 'http://localhost:5003'

    bc1 = blockchain_factory(
        node_name_1,
        'http://localhost:5001',
        100,
        [node_name_2, node_name_3],
    )

    bc2 = blockchain_factory(
        node_name_2,
        'http://localhost:5002',
        100,
        [node_name_1, node_name_3],
    )

    bc3 = blockchain_factory(
        node_name_3,
        'http://localhost:5003',
        100,
        [node_name_1, node_name_2],
    )


    bc1.consensus.add_to_validator_connected(bc2.node)
    bc1.consensus.add_to_validator_connected(bc3.node)
    bc1.consensus.init()

    bc2.consensus.add_to_validator_connected(bc1.node)
    bc2.consensus.add_to_validator_connected(bc3.node)
    bc2.consensus.init()

    bc3.consensus.add_to_validator_connected(bc1.node)
    bc3.consensus.add_to_validator_connected(bc2.node)
    bc3.consensus.init()

    message = Message.new('message')
    diff_data_message = Message(message.message_id, 'diff_message')

    ballot_1 = Ballot.new(node_name_1, message, IsaacState.INIT, BallotVotingResult.agree)
    ballot_id = ballot_1.ballot_id
    ballot_2 = Ballot(ballot_id, node_name_2, message, IsaacState.INIT, BallotVotingResult.agree, ballot_1.timestamp)
    ballot_3 = Ballot(ballot_id, node_name_3, diff_data_message, IsaacState.INIT, BallotVotingResult.agree, ballot_1.timestamp)

    bc1.receive_ballot(ballot_1)
    bc1.receive_ballot(ballot_2)
    bc1.receive_ballot(ballot_3)

    assert bc1.consensus.slot.get_ballot_state(ballot_2) == IsaacState.INIT
