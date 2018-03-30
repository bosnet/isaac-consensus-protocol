from ..common import Ballot, BallotVotingResult, Message
from ..consensus import get_fba_module
from ..consensus.fba.isaac import IsaacState
from .util import blockchain_factory


IsaacConsensus = get_fba_module('isaac').IsaacConsensus


def test_state_lifecycle():
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
    ballot_init_1 = Ballot.new(node_name_1, message, IsaacState.INIT, BallotVotingResult.agree)
    ballot_id = ballot_init_1.ballot_id
    ballot_init_2 = Ballot(ballot_id, node_name_2, message, IsaacState.INIT, BallotVotingResult.agree,
                           ballot_init_1.timestamp)
    ballot_init_3 = Ballot(ballot_id, node_name_3, message, IsaacState.INIT, BallotVotingResult.agree,
                           ballot_init_1.timestamp)

    bc1.receive_ballot(ballot_init_1)
    bc1.receive_ballot(ballot_init_2)
    bc1.receive_ballot(ballot_init_3)

    bc2.receive_ballot(ballot_init_1)
    bc2.receive_ballot(ballot_init_2)
    bc2.receive_ballot(ballot_init_3)

    bc3.receive_ballot(ballot_init_1)
    bc3.receive_ballot(ballot_init_2)
    bc3.receive_ballot(ballot_init_3)

    assert bc1.consensus.slot.get_ballot_state(ballot_init_1) == IsaacState.SIGN
    assert bc2.consensus.slot.get_ballot_state(ballot_init_1) == IsaacState.SIGN
    assert bc3.consensus.slot.get_ballot_state(ballot_init_1) == IsaacState.SIGN

    ballot_sign_1 = Ballot(ballot_id, node_name_1, message, IsaacState.SIGN, BallotVotingResult.agree,
                           ballot_init_1.timestamp)
    ballot_sign_2 = Ballot(ballot_id, node_name_2, message, IsaacState.SIGN, BallotVotingResult.agree,
                           ballot_init_1.timestamp)
    ballot_sign_3 = Ballot(ballot_id, node_name_3, message, IsaacState.SIGN, BallotVotingResult.agree,
                           ballot_init_1.timestamp)

    bc1.receive_ballot(ballot_sign_1)
    bc1.receive_ballot(ballot_sign_2)
    bc1.receive_ballot(ballot_sign_3)

    bc2.receive_ballot(ballot_sign_1)
    bc2.receive_ballot(ballot_sign_2)
    bc2.receive_ballot(ballot_sign_3)

    bc3.receive_ballot(ballot_sign_1)
    bc3.receive_ballot(ballot_sign_2)
    bc3.receive_ballot(ballot_sign_3)

    assert bc1.consensus.slot.get_ballot_state(ballot_init_1) == IsaacState.ACCEPT
    assert bc2.consensus.slot.get_ballot_state(ballot_init_1) == IsaacState.ACCEPT
    assert bc3.consensus.slot.get_ballot_state(ballot_init_1) == IsaacState.ACCEPT

    ballot_accept_1 = Ballot(ballot_id, node_name_1, message, IsaacState.ACCEPT, BallotVotingResult.agree,
                             ballot_init_1.timestamp)
    ballot_accept_2 = Ballot(ballot_id, node_name_2, message, IsaacState.ACCEPT, BallotVotingResult.agree,
                             ballot_init_1.timestamp)
    ballot_accept_3 = Ballot(ballot_id, node_name_3, message, IsaacState.ACCEPT, BallotVotingResult.agree,
                             ballot_init_1.timestamp)

    bc1.receive_ballot(ballot_sign_1)    # different state ballot
    bc1.receive_ballot(ballot_accept_2)
    bc1.receive_ballot(ballot_accept_3)

    bc2.receive_ballot(ballot_accept_1)
    bc2.receive_ballot(ballot_accept_2)
    bc2.receive_ballot(ballot_sign_3)    # different state ballot

    bc3.receive_ballot(ballot_accept_1)
    bc3.receive_ballot(ballot_accept_2)
    bc3.receive_ballot(ballot_accept_3)

    assert message in bc1.consensus.messages
    assert bc2.consensus.slot.get_ballot_state(ballot_init_1) == IsaacState.ACCEPT
    assert message in bc3.consensus.messages
