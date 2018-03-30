from ..common import Ballot, BallotVotingResult, Message
from ..consensus import get_fba_module
from ..consensus.fba.isaac import IsaacState
from ..blockchain.util import blockchain_factory


IsaacConsensus = get_fba_module('isaac').IsaacConsensus


def test_state_ballot_timestamp():
    node_name_1 = 'http://localhost:5001'
    node_name_2 = 'http://localhost:5002'
    node_name_3 = 'http://localhost:5003'

    bc1 = blockchain_factory(
        node_name_1,
        'http://localhost:5001',
        100,
        [node_name_2, node_name_3]
    )

    bc2 = blockchain_factory(
        node_name_2,
        'http://localhost:5002',
        100,
        [node_name_1, node_name_3]
    )

    bc3 = blockchain_factory(
        node_name_3,
        'http://localhost:5003',
        100,
        [node_name_1, node_name_2]
    )

    bc1.consensus.add_to_validator_connected(bc2.node)
    bc1.consensus.add_to_validator_connected(bc3.node)
    bc1.consensus.init()

    message = Message.new('message')
    ballot_init_1 = Ballot.new(node_name_1, message, IsaacState.INIT, BallotVotingResult.agree)
    ballot_id = ballot_init_1.ballot_id
    # ballot with same ballot_id, message, state, voting result, timestamp
    ballot_init_2 = Ballot(ballot_id, node_name_2, message, IsaacState.INIT, BallotVotingResult.agree)
    # ballot with same ballot_id, message, state, voting result but different timestamp
    ballot_init_3 = Ballot(ballot_id, node_name_3, message, IsaacState.INIT, BallotVotingResult.agree,
                           ballot_init_1.timestamp)

    bc1.receive_ballot(ballot_init_1)
    bc1.receive_ballot(ballot_init_2)
    bc1.receive_ballot(ballot_init_3)

    assert ballot_init_1 == bc1.consensus.slot.slot['b0'].validator_ballots[ballot_init_1.node_name]
    assert ballot_init_2.node_name not in bc1.consensus.slot.slot['b0'].validator_ballots
    assert ballot_init_3 == bc1.consensus.slot.slot['b0'].validator_ballots[ballot_init_3.node_name]
