from ..common import Ballot, BallotVotingResult, Message
from ..consensus import get_fba_module
from ..consensus.fba.isaac import IsaacState
from .util import blockchain_factory


IsaacConsensus = get_fba_module('isaac').IsaacConsensus


def test_next_message():
    node_name_1 = 'http://localhost:5001'
    node_name_2 = 'http://localhost:5002'
    node_name_3 = 'http://localhost:5003'
    node_name_4 = 'http://localhost:5004'

    bc1 = blockchain_factory(
        node_name_1,
        'http://localhost:5001',
        100,
        [node_name_2, node_name_3, node_name_4],
    )

    bc2 = blockchain_factory(
        node_name_2,
        'http://localhost:5002',
        100,
        [node_name_1, node_name_3, node_name_4],
    )

    bc3 = blockchain_factory(
        node_name_3,
        'http://localhost:5003',
        100,
        [node_name_1, node_name_2, node_name_4],
    )

    bc4 = blockchain_factory(
        node_name_4,
        'http://localhost:5004',
        100,
        [node_name_1, node_name_2, node_name_3],
    )

    bc1.consensus.add_to_validator_connected(bc2.node)
    bc1.consensus.add_to_validator_connected(bc3.node)
    bc1.consensus.add_to_validator_connected(bc4.node)
    bc1.consensus.init()

    message_1 = Message.new('message-1')

    ballot_init_2 = Ballot.new(node_name_2, message_1, IsaacState.INIT, BallotVotingResult.agree)
    ballot_id = ballot_init_2.ballot_id
    ballot_init_3 = Ballot(ballot_id, node_name_3, message_1, IsaacState.INIT, BallotVotingResult.agree, ballot_init_2.timestamp)
    ballot_init_4 = Ballot(ballot_id, node_name_4, message_1, IsaacState.INIT, BallotVotingResult.agree, ballot_init_2.timestamp)

    bc1.receive_ballot(ballot_init_2)
    bc1.receive_ballot(ballot_init_3)
    bc1.receive_ballot(ballot_init_4)

    assert bc1.consensus.slot.get_ballot_state(ballot_init_2) == IsaacState.SIGN

    ballot_sign_2 = Ballot(ballot_id, node_name_2, message_1, IsaacState.ACCEPT, BallotVotingResult.agree, ballot_init_2.timestamp)
    ballot_sign_3 = Ballot(ballot_id, node_name_3, message_1, IsaacState.SIGN, BallotVotingResult.agree, ballot_init_2.timestamp)
    ballot_sign_4 = Ballot(ballot_id, node_name_4, message_1, IsaacState.SIGN, BallotVotingResult.agree, ballot_init_2.timestamp)

    bc1.receive_ballot(ballot_sign_2)
    bc1.receive_ballot(ballot_sign_3)
    bc1.receive_ballot(ballot_sign_4)

    assert bc1.consensus.slot.get_ballot_state(ballot_init_2) == IsaacState.ACCEPT

    ballot_accept_3 = Ballot(ballot_id, node_name_3, message_1, IsaacState.ACCEPT, BallotVotingResult.agree, ballot_init_2.timestamp)
    ballot_accept_4 = Ballot(ballot_id, node_name_4, message_1, IsaacState.ACCEPT, BallotVotingResult.agree, ballot_init_2.timestamp)

    bc1.receive_ballot(ballot_accept_3)
    bc1.receive_ballot(ballot_accept_4)

    assert message_1 in bc1.consensus.messages

    message_2 = Message.new('message-2')
    ballot_init_2 = Ballot.new(node_name_2, message_2, IsaacState.INIT, BallotVotingResult.agree)
    ballot_id_2 = ballot_init_2.ballot_id
    ballot_timestamp = ballot_init_2.timestamp

    ballot_init_3.ballot_id = ballot_id_2
    ballot_init_4.ballot_id = ballot_id_2
    ballot_init_3.timestamp = ballot_timestamp
    ballot_init_4.timestamp = ballot_timestamp

    ballot_init_2.message = message_2
    ballot_init_3.message = message_2
    ballot_init_4.message = message_2

    bc1.receive_ballot(ballot_init_2)
    bc1.receive_ballot(ballot_init_3)
    bc1.receive_ballot(ballot_init_4)

    assert bc1.consensus.slot.get_ballot_state(ballot_init_2) == IsaacState.SIGN

    ballot_sign_2.ballot_id = ballot_id_2
    ballot_sign_3.ballot_id = ballot_id_2
    ballot_sign_4.ballot_id = ballot_id_2
    ballot_sign_2.timestamp = ballot_timestamp
    ballot_sign_3.timestamp = ballot_timestamp
    ballot_sign_4.timestamp = ballot_timestamp

    ballot_sign_2.message = message_2
    ballot_sign_3.message = message_2
    ballot_sign_4.message = message_2

    bc1.receive_ballot(ballot_sign_2)
    bc1.receive_ballot(ballot_sign_3)
    bc1.receive_ballot(ballot_sign_4)

    assert bc1.consensus.slot.get_ballot_state(ballot_init_2) == IsaacState.ACCEPT

    ballot_accept_3.ballot_id = ballot_id_2
    ballot_accept_4.ballot_id = ballot_id_2

    ballot_accept_3.message = message_2
    ballot_accept_4.message = message_2
    ballot_accept_3.timestamp = ballot_timestamp
    ballot_accept_4.timestamp = ballot_timestamp

    bc1.receive_ballot(ballot_accept_3)
    bc1.receive_ballot(ballot_accept_4)

    assert message_2 in bc1.consensus.messages
