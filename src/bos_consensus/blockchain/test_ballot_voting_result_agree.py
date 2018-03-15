import copy

from ..common import Ballot, BallotVotingResult, Message, node_factory
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


def test_ballot_voting_result_agree():
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

    # make ballot 2 from node 3 with disagree voting result.
    message = Message.new('message')
    ballot_init_1 = Ballot.new(node_name_1, message, IsaacState.INIT, BallotVotingResult.agree)
    ballot_id = ballot_init_1.ballot_id
    ballot_init_2 = Ballot(ballot_id, node_name_2, message, IsaacState.INIT, BallotVotingResult.disagree)
    ballot_init_3 = Ballot(ballot_id, node_name_3, message, IsaacState.INIT, BallotVotingResult.agree)

    bc1.receive_ballot(ballot_init_1)
    bc1.receive_ballot(ballot_init_2)
    bc1.receive_ballot(ballot_init_3)

    # state change to SIGN is not available
    assert bc1.consensus.slot.get_ballot_state(ballot_init_1) != IsaacState.SIGN

    # validator node 2 resend the ballot with agree voting result.
    ballot_init_2.result = BallotVotingResult.agree
    bc1.receive_ballot(ballot_init_2)

    # state is changed to SIGN
    assert bc1.consensus.slot.get_ballot_state(ballot_init_1) == IsaacState.SIGN

    ballot_sign_1 = Ballot(ballot_id, node_name_1, message, IsaacState.SIGN, BallotVotingResult.agree)
    ballot_sign_2 = Ballot(ballot_id, node_name_2, message, IsaacState.SIGN, BallotVotingResult.agree)
    ballot_sign_3 = Ballot(ballot_id, node_name_3, message, IsaacState.SIGN, BallotVotingResult.disagree)

    bc1.receive_ballot(ballot_sign_1)
    bc1.receive_ballot(ballot_sign_2)
    bc1.receive_ballot(ballot_sign_3)

    assert bc1.consensus.slot.get_ballot_state(ballot_sign_1) != IsaacState.ACCEPT

    ballot_sign_3.result = BallotVotingResult.agree
    bc1.receive_ballot(ballot_sign_3)

    assert bc1.consensus.slot.get_ballot_state(ballot_sign_3) == IsaacState.ACCEPT

    ballot_accept_1 = Ballot(ballot_id, node_name_1, message, IsaacState.ACCEPT, BallotVotingResult.agree)
    ballot_accept_2 = Ballot(ballot_id, node_name_2, message, IsaacState.ACCEPT, BallotVotingResult.agree)
    ballot_accept_3 = Ballot(ballot_id, node_name_3, message, IsaacState.ACCEPT, BallotVotingResult.agree)

    bc1.receive_ballot(ballot_accept_1)
    bc1.receive_ballot(ballot_accept_2)
    bc1.receive_ballot(ballot_accept_3)

    assert message in bc1.consensus.messages