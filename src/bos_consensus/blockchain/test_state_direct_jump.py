from ..common import Ballot, BallotVotingResult, Message
from ..consensus import get_fba_module
from ..consensus.fba.isaac import IsaacState
from .util import blockchain_factory


IsaacConsensus = get_fba_module('isaac').IsaacConsensus


def test_state_direct_sign_to_allcomfirm():
    node_name_1 = 'http://localhost:5001'
    node_name_2 = 'http://localhost:5002'
    node_name_3 = 'http://localhost:5003'
    node_name_4 = 'http://localhost:5004'

    bc1 = blockchain_factory(
        node_name_1,
        'http://localhost:5001',
        60,
        [node_name_2, node_name_3, node_name_4],
    )

    bc2 = blockchain_factory(
        node_name_2,
        'http://localhost:5002',
        60,
        [node_name_1, node_name_3, node_name_4],
    )

    bc3 = blockchain_factory(
        node_name_3,
        'http://localhost:5003',
        60,
        [node_name_1, node_name_2, node_name_4],
    )

    bc4 = blockchain_factory(
        node_name_4,
        'http://localhost:5004',
        60,
        [node_name_1, node_name_2, node_name_3],
    )

    bc1.consensus.add_to_validator_connected(bc2.node)
    bc1.consensus.add_to_validator_connected(bc3.node)
    bc1.consensus.add_to_validator_connected(bc4.node)
    bc1.consensus.init()

    message = Message.new('message')
    ballot_init_2 = Ballot.new(node_name_2, message, IsaacState.INIT, BallotVotingResult.agree)
    ballot_id = ballot_init_2.ballot_id
    ballot_init_3 = Ballot(ballot_id, node_name_3, message, IsaacState.INIT, BallotVotingResult.agree)
    ballot_init_4 = Ballot(ballot_id, node_name_4, message, IsaacState.INIT, BallotVotingResult.agree)

    bc1.receive_ballot(ballot_init_2)
    bc1.receive_ballot(ballot_init_3)
    bc1.receive_ballot(ballot_init_4)

    assert bc1.consensus.slot.get_ballot_state(ballot_init_2) == IsaacState.SIGN

    ballot_sign_2 = Ballot(ballot_id, node_name_2, message, IsaacState.ACCEPT, BallotVotingResult.agree)
    ballot_sign_3 = Ballot(ballot_id, node_name_3, message, IsaacState.ALLCONFIRM, BallotVotingResult.agree)
    ballot_sign_4 = Ballot(ballot_id, node_name_4, message, IsaacState.ALLCONFIRM, BallotVotingResult.agree)

    bc1.receive_ballot(ballot_sign_2)
    bc1.receive_ballot(ballot_sign_3)
    bc1.receive_ballot(ballot_sign_4)

    assert message in bc1.consensus.messages

    message2 = Message.new('message2')
    ballot_init_2 = Ballot.new(node_name_2, message2, IsaacState.INIT, BallotVotingResult.agree)
    ballot_id = ballot_init_2.ballot_id
    ballot_init_3 = Ballot(ballot_id, node_name_3, message2, IsaacState.INIT, BallotVotingResult.agree)
    ballot_init_4 = Ballot(ballot_id, node_name_4, message2, IsaacState.INIT, BallotVotingResult.agree)

    bc1.receive_ballot(ballot_init_2)
    bc1.receive_ballot(ballot_init_3)
    bc1.receive_ballot(ballot_init_4)

    assert bc1.consensus.slot.get_ballot_state(ballot_init_2) == IsaacState.SIGN

    ballot_sign_2 = Ballot(ballot_id, node_name_2, message2, IsaacState.SIGN, BallotVotingResult.agree)
    ballot_sign_3 = Ballot(ballot_id, node_name_3, message2, IsaacState.SIGN, BallotVotingResult.agree)
    ballot_accept_4 = Ballot(ballot_id, node_name_4, message2, IsaacState.ACCEPT, BallotVotingResult.agree)

    bc1.receive_ballot(ballot_sign_2)
    bc1.receive_ballot(ballot_sign_3)
    bc1.receive_ballot(ballot_accept_4)

    assert bc1.consensus.slot.get_ballot_state(ballot_init_2) == IsaacState.ACCEPT

    ballot_accept_2 = Ballot(ballot_id, node_name_2, message2, IsaacState.ACCEPT, BallotVotingResult.agree)

    bc1.receive_ballot(ballot_accept_2)

    assert message2 in bc1.consensus.messages
