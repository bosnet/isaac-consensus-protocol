from ..common.ballot import Ballot
from ..network import BaseTransport, Endpoint
from ..blockchain import Blockchain
from ..consensus import get_fba_module
from ..common.node import node_factory
from ..consensus.fba.isaac import IsaacState
from ..common.message import Message


IsaacConsensus = get_fba_module('isaac').IsaacConsensus


class StubTransport(BaseTransport):
    def send(self, _, __):
        return


def blockchain_factory(name, address, threshold, validator_endpoint_uris):
    node = node_factory(name, Endpoint.from_uri(address))
    validators = list()
    for uri in validator_endpoint_uris:
        validators.append(
            node_factory(uri, Endpoint.from_uri(uri)),
        )

    consensus = IsaacConsensus(node, threshold, validators)
    return Blockchain(
        consensus,
        StubTransport()
    )


def test_consensus_instantiation():
    blockchain = blockchain_factory(
        'n1',
        'http://localhost:5001',
        100,
        ['http://localhost:5002', 'http://localhost:5003'])

    assert blockchain.node_name == 'n1'
    assert blockchain.endpoint.uri_full == 'http://localhost:5001?name=n1'
    assert blockchain.consensus.threshold == 100


def test_state_init():
    blockchain = blockchain_factory(
        'n1',
        'http://localhost:5001',
        100,
        ['http://localhost:5002', 'http://localhost:5003'])

    assert blockchain.get_state() == IsaacState.INIT


IsaacConsensus.transport = StubTransport()


def test_state_init_to_sign():
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

    bc1.consensus.add_to_validators(bc2.node)
    bc1.consensus.add_to_validators(bc3.node)
    bc1.consensus.init()

    message = Message.new('message')
    ballot_init_1 = Ballot.new(node_name_1, message, IsaacState.INIT)
    ballot_init_2 = Ballot.new(node_name_2, message, IsaacState.INIT)
    ballot_init_3 = Ballot.new(node_name_3, message, IsaacState.INIT)

    bc1.receive_ballot(ballot_init_1)
    bc1.receive_ballot(ballot_init_2)
    bc1.receive_ballot(ballot_init_3)

    assert bc1.get_state() == IsaacState.SIGN


def test_state_init_to_all_confirm_sequence():
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

    bc1.consensus.add_to_validators(bc2.node)
    bc1.consensus.add_to_validators(bc3.node)
    bc1.consensus.init()

    bc2.consensus.add_to_validators(bc1.node)
    bc2.consensus.add_to_validators(bc3.node)
    bc2.consensus.init()

    bc3.consensus.add_to_validators(bc1.node)
    bc3.consensus.add_to_validators(bc2.node)
    bc3.consensus.init()

    message = Message.new('message')
    ballot_init_1 = Ballot.new(node_name_1, message, IsaacState.INIT)
    ballot_init_2 = Ballot.new(node_name_2, message, IsaacState.INIT)
    ballot_init_3 = Ballot.new(node_name_3, message, IsaacState.INIT)

    bc1.receive_ballot(ballot_init_1)
    bc1.receive_ballot(ballot_init_2)
    bc1.receive_ballot(ballot_init_3)

    bc2.receive_ballot(ballot_init_1)
    bc2.receive_ballot(ballot_init_2)
    bc2.receive_ballot(ballot_init_3)

    bc3.receive_ballot(ballot_init_1)
    bc3.receive_ballot(ballot_init_2)
    bc3.receive_ballot(ballot_init_3)

    assert bc1.get_state() == IsaacState.SIGN
    assert bc2.get_state() == IsaacState.SIGN
    assert bc3.get_state() == IsaacState.SIGN

    ballot_sign_1 = Ballot.new(node_name_1, message, IsaacState.SIGN)
    ballot_sign_2 = Ballot.new(node_name_2, message, IsaacState.SIGN)
    ballot_sign_3 = Ballot.new(node_name_3, message, IsaacState.SIGN)

    bc1.receive_ballot(ballot_sign_1)
    bc1.receive_ballot(ballot_sign_2)
    bc1.receive_ballot(ballot_sign_3)

    bc2.receive_ballot(ballot_sign_1)
    bc2.receive_ballot(ballot_sign_2)
    bc2.receive_ballot(ballot_sign_3)

    bc3.receive_ballot(ballot_sign_1)
    bc3.receive_ballot(ballot_sign_2)
    bc3.receive_ballot(ballot_sign_3)

    assert bc1.get_state() == IsaacState.ACCEPT
    assert bc2.get_state() == IsaacState.ACCEPT
    assert bc3.get_state() == IsaacState.ACCEPT

    ballot_accept_1 = Ballot.new(node_name_1, message, IsaacState.ACCEPT)
    ballot_accept_2 = Ballot.new(node_name_2, message, IsaacState.ACCEPT)
    ballot_accept_3 = Ballot.new(node_name_3, message, IsaacState.ACCEPT)

    bc1.receive_ballot(ballot_sign_1)    # different state ballot
    bc1.receive_ballot(ballot_accept_2)
    bc1.receive_ballot(ballot_accept_3)

    bc2.receive_ballot(ballot_accept_1)
    bc2.receive_ballot(ballot_accept_2)
    bc2.receive_ballot(ballot_sign_3)    # different state ballot

    bc3.receive_ballot(ballot_accept_1)
    bc3.receive_ballot(ballot_accept_2)
    bc3.receive_ballot(ballot_accept_3)

    assert bc1.get_state() == IsaacState.ALLCONFIRM
    assert bc2.get_state() == IsaacState.ACCEPT
    assert bc3.get_state() == IsaacState.ALLCONFIRM


def test_state_jump_from_init():
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

    bc1.consensus.add_to_validators(bc2.node)
    bc1.consensus.add_to_validators(bc3.node)
    bc1.consensus.add_to_validators(bc4.node)
    bc1.consensus.init()

    message = Message.new('message')
    ballot_init_2 = Ballot.new(node_name_2, message, IsaacState.INIT)
    ballot_init_3 = Ballot.new(node_name_3, message, IsaacState.INIT)
    ballot_init_4 = Ballot.new(node_name_4, message, IsaacState.INIT)

    bc1.receive_ballot(ballot_init_2)
    bc1.receive_ballot(ballot_init_3)
    bc1.receive_ballot(ballot_init_4)

    assert bc1.get_state() == IsaacState.SIGN

    ballot_sign_2 = Ballot.new(node_name_2, message, IsaacState.ACCEPT)
    ballot_sign_3 = Ballot.new(node_name_3, message, IsaacState.SIGN)
    ballot_sign_4 = Ballot.new(node_name_4, message, IsaacState.SIGN)

    bc1.receive_ballot(ballot_sign_2)
    bc1.receive_ballot(ballot_sign_3)
    bc1.receive_ballot(ballot_sign_4)

    assert bc1.get_state() == IsaacState.ACCEPT

    ballot_accept_3 = Ballot.new(node_name_3, message, IsaacState.ACCEPT)
    ballot_accept_4 = Ballot.new(node_name_4, message, IsaacState.ACCEPT)

    bc1.receive_ballot(ballot_accept_3)
    bc1.receive_ballot(ballot_accept_4)

    assert bc1.get_state() == IsaacState.ALLCONFIRM


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

    bc1.consensus.add_to_validators(bc2.node)
    bc1.consensus.add_to_validators(bc3.node)
    bc1.consensus.add_to_validators(bc4.node)
    bc1.consensus.init()

    message_1 = Message.new('message-1')

    ballot_init_2 = Ballot.new(node_name_2, message_1, IsaacState.INIT)
    ballot_init_3 = Ballot.new(node_name_3, message_1, IsaacState.INIT)
    ballot_init_4 = Ballot.new(node_name_4, message_1, IsaacState.INIT)

    bc1.receive_ballot(ballot_init_2)
    bc1.receive_ballot(ballot_init_3)
    bc1.receive_ballot(ballot_init_4)

    assert bc1.get_state() == IsaacState.SIGN

    ballot_sign_2 = Ballot.new(node_name_2, message_1, IsaacState.ACCEPT)
    ballot_sign_3 = Ballot.new(node_name_3, message_1, IsaacState.SIGN)
    ballot_sign_4 = Ballot.new(node_name_4, message_1, IsaacState.SIGN)

    bc1.receive_ballot(ballot_sign_2)
    bc1.receive_ballot(ballot_sign_3)
    bc1.receive_ballot(ballot_sign_4)

    assert bc1.get_state() == IsaacState.ACCEPT

    ballot_accept_3 = Ballot.new(node_name_3, message_1, IsaacState.ACCEPT)
    ballot_accept_4 = Ballot.new(node_name_4, message_1, IsaacState.ACCEPT)

    bc1.receive_ballot(ballot_accept_3)
    bc1.receive_ballot(ballot_accept_4)

    assert bc1.get_state() == IsaacState.ALLCONFIRM

    message_2 = Message.new('message-2')

    ballot_init_2.message = message_2
    ballot_init_3.message = message_2
    ballot_init_4.message = message_2

    bc1.receive_ballot(ballot_init_2)
    bc1.receive_ballot(ballot_init_3)
    bc1.receive_ballot(ballot_init_4)

    assert bc1.get_state() == IsaacState.SIGN

    ballot_sign_2.message = message_2
    ballot_sign_3.message = message_2
    ballot_sign_4.message = message_2

    bc1.receive_ballot(ballot_sign_2)
    bc1.receive_ballot(ballot_sign_3)
    bc1.receive_ballot(ballot_sign_4)

    assert bc1.get_state() == IsaacState.ACCEPT

    ballot_accept_3.message = message_2
    ballot_accept_4.message = message_2

    bc1.receive_ballot(ballot_accept_3)
    bc1.receive_ballot(ballot_accept_4)

    assert bc1.get_state() == IsaacState.ALLCONFIRM
