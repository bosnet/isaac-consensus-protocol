import copy

from ..common import Ballot, Message, node_factory
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


def test_multiple_ballot_init_to_all_confirm_sequence():
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

    # validator configuration
    bc1.consensus.add_to_validator_connected(bc2.node)
    bc1.consensus.add_to_validator_connected(bc3.node)
    bc1.consensus.init()

    bc2.consensus.add_to_validator_connected(bc1.node)
    bc2.consensus.add_to_validator_connected(bc3.node)
    bc2.consensus.init()

    bc3.consensus.add_to_validator_connected(bc1.node)
    bc3.consensus.add_to_validator_connected(bc2.node)
    bc3.consensus.init()

    # make ballot 1
    message = Message.new('message')
    ballot_11 = Ballot.new(node_name_1, message, IsaacState.INIT)
    ballot_id_1 = ballot_11.ballot_id
    ballot_12 = Ballot(ballot_id_1, node_name_2, message, IsaacState.INIT)
    ballot_13 = Ballot(ballot_id_1, node_name_3, message, IsaacState.INIT)

    # make ballot 2
    message2 = Message.new('message2')
    ballot_21 = Ballot.new(node_name_1, message2, IsaacState.INIT)
    ballot_id_2 = ballot_21.ballot_id
    ballot_22 = Ballot(ballot_id_2, node_name_2, message2, IsaacState.INIT)
    ballot_23 = Ballot(ballot_id_2, node_name_3, message2, IsaacState.INIT)

    # receive ballot 1 and 2 simultaniously
    bc1.receive_ballot(ballot_11)
    bc1.receive_ballot(ballot_21)
    bc1.receive_ballot(ballot_12)
    bc1.receive_ballot(ballot_22)
    bc1.receive_ballot(ballot_13)
    bc1.receive_ballot(ballot_23)

    bc2.receive_ballot(ballot_11)
    bc2.receive_ballot(ballot_21)
    bc2.receive_ballot(ballot_12)
    bc2.receive_ballot(ballot_22)
    bc2.receive_ballot(ballot_13)
    bc2.receive_ballot(ballot_23)

    bc3.receive_ballot(ballot_11)
    bc3.receive_ballot(ballot_21)
    bc3.receive_ballot(ballot_12)
    bc3.receive_ballot(ballot_22)
    bc3.receive_ballot(ballot_13)
    bc3.receive_ballot(ballot_23)

    # check both ballot 1 and 2 in slot
    assert bc1.consensus.slot.get_ballot_state(ballot_11) == IsaacState.SIGN
    assert bc2.consensus.slot.get_ballot_state(ballot_11) == IsaacState.SIGN
    assert bc3.consensus.slot.get_ballot_state(ballot_11) == IsaacState.SIGN

    assert bc1.consensus.slot.get_ballot_state(ballot_21) == IsaacState.SIGN
    assert bc2.consensus.slot.get_ballot_state(ballot_21) == IsaacState.SIGN
    assert bc3.consensus.slot.get_ballot_state(ballot_21) == IsaacState.SIGN

    # make ballot 1 with SIGN state
    ballot_11.state = IsaacState.SIGN
    ballot_12.state = IsaacState.SIGN
    ballot_13.state = IsaacState.SIGN

    # make ballot 2 with SIGN state
    ballot_21.state = IsaacState.SIGN
    ballot_22.state = IsaacState.SIGN
    ballot_23.state = IsaacState.SIGN

    # receive ballot 1 and 2 simultaniously
    bc1.receive_ballot(ballot_11)
    bc1.receive_ballot(ballot_21)
    bc1.receive_ballot(ballot_12)
    bc1.receive_ballot(ballot_22)
    bc1.receive_ballot(ballot_13)
    bc1.receive_ballot(ballot_23)

    bc2.receive_ballot(ballot_11)
    bc2.receive_ballot(ballot_21)
    bc2.receive_ballot(ballot_12)
    bc2.receive_ballot(ballot_22)
    bc2.receive_ballot(ballot_13)
    bc2.receive_ballot(ballot_23)

    bc3.receive_ballot(ballot_11)
    bc3.receive_ballot(ballot_21)
    bc3.receive_ballot(ballot_12)
    bc3.receive_ballot(ballot_22)
    bc3.receive_ballot(ballot_13)
    bc3.receive_ballot(ballot_23)

    # check both ballot 1 and 2 in slot
    assert bc1.consensus.slot.get_ballot_state(ballot_11) == IsaacState.ACCEPT
    assert bc2.consensus.slot.get_ballot_state(ballot_11) == IsaacState.ACCEPT
    assert bc3.consensus.slot.get_ballot_state(ballot_11) == IsaacState.ACCEPT

    assert bc1.consensus.slot.get_ballot_state(ballot_21) == IsaacState.ACCEPT
    assert bc2.consensus.slot.get_ballot_state(ballot_21) == IsaacState.ACCEPT
    assert bc3.consensus.slot.get_ballot_state(ballot_21) == IsaacState.ACCEPT

    # make ballot 1 with ACCEPT state
    ballot_11.state = IsaacState.ACCEPT
    ballot_12.state = IsaacState.ACCEPT
    ballot_13.state = IsaacState.ACCEPT

    # make ballot 2 with ACCEPT state
    ballot_21.state = IsaacState.ACCEPT
    ballot_22.state = IsaacState.ACCEPT
    ballot_23.state = IsaacState.ACCEPT

    bc1.receive_ballot(ballot_11)
    bc1.receive_ballot(ballot_21)
    bc1.receive_ballot(ballot_12)
    bc1.receive_ballot(ballot_22)
    bc1.receive_ballot(ballot_13)
    bc1.receive_ballot(ballot_23)

    bc2.receive_ballot(ballot_11)
    bc2.receive_ballot(ballot_21)
    bc2.receive_ballot(ballot_12)
    bc2.receive_ballot(ballot_22)
    bc2.receive_ballot(ballot_13)
    bc2.receive_ballot(ballot_23)

    bc3.receive_ballot(ballot_11)
    bc3.receive_ballot(ballot_21)
    bc3.receive_ballot(ballot_12)
    bc3.receive_ballot(ballot_22)
    bc3.receive_ballot(ballot_13)
    bc3.receive_ballot(ballot_23)
    
    # check all confirm by save message
    assert message in bc1.consensus.messages
    assert message2 in bc1.consensus.messages

    assert message in bc2.consensus.messages
    assert message2 in bc2.consensus.messages

    assert message in bc3.consensus.messages
    assert message2 in bc3.consensus.messages


def test_multiple_ballot_jump_from_init():
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

    # make ballot 1
    message = Message.new('message')
    ballot_12 = Ballot.new(node_name_2, message, IsaacState.INIT)
    ballot_id = ballot_12.ballot_id
    ballot_13 = Ballot(ballot_id, node_name_3, message, IsaacState.INIT)
    ballot_14 = Ballot(ballot_id, node_name_4, message, IsaacState.INIT)

    # make ballot 2
    message2 = Message.new('message2')
    ballot_22 = Ballot.new(node_name_2, message2, IsaacState.INIT)
    ballot_id_2 = ballot_22.ballot_id
    ballot_23 = Ballot(ballot_id_2, node_name_3, message2, IsaacState.INIT)
    ballot_24 = Ballot(ballot_id_2, node_name_4, message2, IsaacState.INIT)

    bc1.receive_ballot(ballot_12)
    bc1.receive_ballot(ballot_13)
    bc1.receive_ballot(ballot_14)

    bc1.receive_ballot(ballot_22)
    bc1.receive_ballot(ballot_23)
    bc1.receive_ballot(ballot_24)

    assert bc1.consensus.slot.get_ballot_state(ballot_12) == IsaacState.SIGN
    assert bc1.consensus.slot.get_ballot_state(ballot_22) == IsaacState.SIGN

    # make ballot 1 with ACCEPT or SIGN state
    ballot_12.state = IsaacState.ACCEPT
    ballot_13.state = IsaacState.SIGN
    ballot_14.state = IsaacState.SIGN

    # make ballot 1 with ACCEPT or SIGN state
    ballot_22.state = IsaacState.ACCEPT
    ballot_23.state = IsaacState.SIGN
    ballot_24.state = IsaacState.SIGN
    
    bc1.receive_ballot(ballot_12)
    bc1.receive_ballot(ballot_13)
    bc1.receive_ballot(ballot_14)

    bc1.receive_ballot(ballot_22)
    bc1.receive_ballot(ballot_23)
    bc1.receive_ballot(ballot_24)

    assert bc1.consensus.slot.get_ballot_state(ballot_12) == IsaacState.ACCEPT
    assert bc1.consensus.slot.get_ballot_state(ballot_22) == IsaacState.ACCEPT

    # make ballot 1 with ACCEPT state
    ballot_13.state = IsaacState.ACCEPT
    ballot_14.state = IsaacState.ACCEPT

    # make ballot 2 with ACCEPT state
    ballot_23.state = IsaacState.ACCEPT
    ballot_24.state = IsaacState.ACCEPT

    bc1.receive_ballot(ballot_13)
    bc1.receive_ballot(ballot_14)

    bc1.receive_ballot(ballot_23)
    bc1.receive_ballot(ballot_24)

    # check all confirm by save message
    assert message in bc1.consensus.messages
    assert message2 in bc1.consensus.messages


def test_multiple_ballot_after_allconfirm():
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

    # make ballot 1
    message_1 = Message.new('message-1')

    ballot_12 = Ballot.new(node_name_2, message_1, IsaacState.INIT)
    ballot_id = ballot_12.ballot_id
    ballot_13 = Ballot(ballot_id, node_name_3, message_1, IsaacState.INIT)
    ballot_14 = Ballot(ballot_id, node_name_4, message_1, IsaacState.INIT)

    # make ballot 2
    message_2 = Message.new('message-2')

    ballot_22 = Ballot.new(node_name_2, message_2, IsaacState.INIT)
    ballot_id_2 = ballot_22.ballot_id
    ballot_23 = Ballot(ballot_id_2, node_name_3, message_2, IsaacState.INIT)
    ballot_24 = Ballot(ballot_id_2, node_name_4, message_2, IsaacState.INIT)

    bc1.receive_ballot(ballot_12)
    bc1.receive_ballot(ballot_13)
    bc1.receive_ballot(ballot_14)

    bc1.receive_ballot(ballot_22)
    bc1.receive_ballot(ballot_23)
    bc1.receive_ballot(ballot_24)

    assert bc1.consensus.slot.get_ballot_state(ballot_12) == IsaacState.SIGN
    assert bc1.consensus.slot.get_ballot_state(ballot_22) == IsaacState.SIGN

    # make ballot 1 with ACCEPT or SIGN state
    ballot_12.state = IsaacState.ACCEPT
    ballot_13.state = IsaacState.SIGN
    ballot_14.state = IsaacState.SIGN

    # make ballot 2 with ACCEPT or SIGN state
    ballot_22.state = IsaacState.ACCEPT
    ballot_23.state = IsaacState.SIGN
    ballot_24.state = IsaacState.SIGN

    bc1.receive_ballot(ballot_12)
    bc1.receive_ballot(ballot_13)
    bc1.receive_ballot(ballot_14)

    bc1.receive_ballot(ballot_22)
    bc1.receive_ballot(ballot_23)
    bc1.receive_ballot(ballot_24)

    assert bc1.consensus.slot.get_ballot_state(ballot_12) == IsaacState.ACCEPT
    assert bc1.consensus.slot.get_ballot_state(ballot_22) == IsaacState.ACCEPT

    ballot_13.state = IsaacState.ACCEPT
    ballot_14.state = IsaacState.ACCEPT

    ballot_23.state = IsaacState.ACCEPT
    ballot_24.state = IsaacState.ACCEPT

    bc1.receive_ballot(ballot_13)
    bc1.receive_ballot(ballot_14)

    bc1.receive_ballot(ballot_23)
    bc1.receive_ballot(ballot_24)

    # check all confirm by save message
    assert message_1 in bc1.consensus.messages
    assert message_2 in bc1.consensus.messages

    message_3 = Message.new('message-3')

    ballot_32 = Ballot.new(node_name_2, message_3, IsaacState.INIT)
    ballot_id_3 = ballot_32.ballot_id
    ballot_33 = Ballot(ballot_id_3, node_name_3, message_3, IsaacState.INIT)
    ballot_34 = Ballot(ballot_id_3, node_name_4, message_3, IsaacState.INIT)

    message_4 = Message.new('message-4')

    ballot_42 = Ballot.new(node_name_2, message_4, IsaacState.INIT)
    ballot_id_4 = ballot_42.ballot_id
    ballot_43 = Ballot(ballot_id_4, node_name_3, message_4, IsaacState.INIT)
    ballot_44 = Ballot(ballot_id_4, node_name_4, message_4, IsaacState.INIT)

    bc1.receive_ballot(ballot_32)
    bc1.receive_ballot(ballot_33)
    bc1.receive_ballot(ballot_34)

    bc1.receive_ballot(ballot_42)
    bc1.receive_ballot(ballot_43)
    bc1.receive_ballot(ballot_44)

    assert bc1.consensus.slot.get_ballot_state(ballot_32) == IsaacState.SIGN
    assert bc1.consensus.slot.get_ballot_state(ballot_42) == IsaacState.SIGN

    ballot_32.state = IsaacState.ACCEPT
    ballot_33.state = IsaacState.SIGN
    ballot_34.state = IsaacState.SIGN

    ballot_42.state = IsaacState.ACCEPT
    ballot_43.state = IsaacState.SIGN
    ballot_44.state = IsaacState.SIGN

    bc1.receive_ballot(ballot_32)
    bc1.receive_ballot(ballot_33)
    bc1.receive_ballot(ballot_34)

    bc1.receive_ballot(ballot_42)
    bc1.receive_ballot(ballot_43)
    bc1.receive_ballot(ballot_44)

    assert bc1.consensus.slot.get_ballot_state(ballot_32) == IsaacState.ACCEPT

    ballot_33.state = IsaacState.ACCEPT
    ballot_34.state = IsaacState.ACCEPT

    ballot_43.state = IsaacState.ACCEPT
    ballot_44.state = IsaacState.ACCEPT

    bc1.receive_ballot(ballot_33)
    bc1.receive_ballot(ballot_34)

    bc1.receive_ballot(ballot_43)
    bc1.receive_ballot(ballot_44)

    # check all confirm by save message
    assert message_3 in bc1.consensus.messages
    assert message_4 in bc1.consensus.messages
