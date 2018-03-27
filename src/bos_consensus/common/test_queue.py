import copy
import datetime

from .slot import Slot
from ..util import get_uuid

from ..common import Ballot, BallotVotingResult, Message, node_factory
from ..network import Endpoint
from ..blockchain import Blockchain
from ..consensus import get_fba_module
from ..consensus.fba.isaac import IsaacState
from ..blockchain.util import StubTransport

IsaacConsensus = get_fba_module('isaac').IsaacConsensus

slot_size = 2


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


def test_queue_data_correctness():
    queue_size = 2
    s0 = Slot(slot_size, queue_size)
    q0 = Ballot(get_uuid(), 1, Message.new(get_uuid()), IsaacState.SIGN)
    q1 = Ballot(get_uuid(), 1, Message.new(get_uuid()), IsaacState.ACCEPT)

    s0.send_to_queue(q0)
    s0.send_to_queue(q1)

    get_ballot_from_queue_0 = s0.slot_queue.get()
    assert get_ballot_from_queue_0.timestamp is q0.timestamp
    assert get_ballot_from_queue_0.message.message_id is q0.message.message_id
    assert get_ballot_from_queue_0.message.data is q0.message.data
    s0.slot_queue.task_done()

    get_ballot_from_queue_1 = s0.slot_queue.get()
    assert get_ballot_from_queue_1.timestamp is q1.timestamp
    assert get_ballot_from_queue_1.message.message_id is q1.message.message_id
    assert get_ballot_from_queue_1.message.data is q1.message.data
    s0.slot_queue.task_done()

    assert s0.slot_queue.empty() is True


def test_queue_in_time_order():
    queue_size = 5
    s0 = Slot(slot_size, queue_size)
    test_q_timestamp_00 = datetime.datetime(2018, 1, 1, 1, 1, 1, 1)  # should be 2nd queue after time order
    test_q_timestamp_01 = datetime.datetime(2019, 12, 11, 2, 10, 1, 1)  # should be last queue after time order
    test_q_timestamp_02 = datetime.datetime(1018, 1, 20, 3, 1, 1, 11)  # should be first queue after time order
    test_q_timestamp_03 = datetime.datetime(2018, 1, 12, 13, 2, 1, 11)  # should be 4th queue after time order
    test_q_timestamp_04 = datetime.datetime(2018, 1, 1, 1, 1, 1, 2)  # should be 3rd queue after time order

    # after order, Queue sequence should be
    # 02-00-04-03-01
    queue00 = Ballot('test0', 0, Message.new(0), IsaacState.ACCEPT, BallotVotingResult.agree, test_q_timestamp_00)
    queue01 = Ballot('test1', 1, Message.new(1), IsaacState.SIGN, BallotVotingResult.agree, test_q_timestamp_01)
    queue02 = Ballot('test2', 2, Message.new(2), IsaacState.INIT, BallotVotingResult.agree, test_q_timestamp_02)
    queue03 = Ballot('test3', 3, Message.new(3), IsaacState.SIGN, BallotVotingResult.agree, test_q_timestamp_03)
    queue04 = Ballot('test4', 4, Message.new(4), IsaacState.ACCEPT, BallotVotingResult.agree, test_q_timestamp_04)

    s0.send_to_queue(queue00)
    s0.send_to_queue(queue01)
    s0.send_to_queue(queue02)
    s0.send_to_queue(queue03)
    s0.send_to_queue(queue04)

    get_queue_00 = s0.slot_queue.get()
    assert get_queue_00.timestamp is queue02.timestamp
    assert 2 is queue02.message.data
    s0.slot_queue.task_done()

    get_queue_01 = s0.slot_queue.get()
    assert get_queue_01.timestamp is queue00.timestamp
    assert 0 is queue00.message.data
    s0.slot_queue.task_done()

    get_queue_02 = s0.slot_queue.get()
    assert get_queue_02.timestamp is queue04.timestamp
    assert 4 is queue04.message.data
    s0.slot_queue.task_done()

    get_queue_03 = s0.slot_queue.get()
    assert get_queue_03.timestamp is queue03.timestamp
    assert 3 is queue03.message.data
    s0.slot_queue.task_done()

    get_queue_04 = s0.slot_queue.get()
    assert get_queue_04.timestamp is queue01.timestamp
    assert 1 is queue01.message.data
    s0.slot_queue.task_done()


def test_queues_get():
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
    message1 = Message.new('message_1')
    ballot_for_slot_1 = Ballot.new(node_name_1, message1, IsaacState.INIT)
    bc1.receive_ballot(ballot_for_slot_1)
    index1 = bc1.consensus.slot.get_ballot_index(ballot_for_slot_1)

    # make ballot 2
    message2 = Message.new('message_2')
    ballot_for_slot_2 = Ballot.new(node_name_1, message2, IsaacState.INIT)
    bc1.receive_ballot(ballot_for_slot_2)
    index2 = bc1.consensus.slot.get_ballot_index(ballot_for_slot_2)

    assert bc1.consensus.slot.slot[index1].is_full is True
    assert bc1.consensus.slot.slot[index2].is_full is True
    assert node_name_1 in bc1.consensus.slot.slot[index1].validator_ballots
    assert node_name_1 in bc1.consensus.slot.slot[index2].validator_ballots
    assert ballot_for_slot_1.ballot_id is bc1.consensus.slot.slot[index1].validator_ballots[node_name_1].ballot_id
    assert ballot_for_slot_2.ballot_id is bc1.consensus.slot.slot[index2].validator_ballots[node_name_1].ballot_id

    # make ballot 2
    queue_message1 = Message.new('Q_message1')
    ballot_from_queue = bc1.consensus.slot.slot_queue
    ballot_for_queue_00 = Ballot.new(node_name_1, queue_message1, IsaacState.INIT)
    bc1.receive_ballot(ballot_for_queue_00)

    # make queue 2
    queue_message2 = Message.new('Q_message2')
    ballot_for_queue_11 = Ballot.new(node_name_1, queue_message2, IsaacState.INIT)
    bc1.receive_ballot(ballot_for_queue_11)

    assert ballot_from_queue.full() is True
    ballot_from_queue00 = bc1.consensus.slot.slot_queue.get()
    ballot_from_queue01 = bc1.consensus.slot.slot_queue.get()

    assert ballot_from_queue00.ballot_id is ballot_for_queue_00.ballot_id
    assert ballot_from_queue01.ballot_id is ballot_for_queue_11.ballot_id


def test_queue_is_make_consensus():
    # set slot size =2
    # set queue size = 2
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
    message = Message.new('message_1')
    test_time_for_slot_1 = datetime.datetime.now()
    ballot_for_slot_11 = Ballot.new(node_name_1, message, IsaacState.INIT, BallotVotingResult.agree, test_time_for_slot_1)
    ballot_id_1 = ballot_for_slot_11.ballot_id
    ballot_for_slot_12 = Ballot(ballot_id_1, node_name_2, message, IsaacState.INIT, BallotVotingResult.agree, test_time_for_slot_1)
    ballot_for_slot_13 = Ballot(ballot_id_1, node_name_3, message, IsaacState.INIT, BallotVotingResult.agree, test_time_for_slot_1)

    # make ballot 2
    message2= Message.new('message_2')
    test_time_for_slot_2 = datetime.datetime.now()
    ballot_for_slot_21 = Ballot.new(node_name_1, message2, IsaacState.INIT, BallotVotingResult.agree, test_time_for_slot_2)
    ballot_id_2 = ballot_for_slot_21.ballot_id
    ballot_for_slot_22 = Ballot(ballot_id_2, node_name_2, message2, IsaacState.INIT, BallotVotingResult.agree, test_time_for_slot_2)
    ballot_for_slot_23 = Ballot(ballot_id_2, node_name_3, message2, IsaacState.INIT, BallotVotingResult.agree, test_time_for_slot_2)

    # make queue 1
    queue_message1 = Message.new('Q_message1')
    test_time_for_queue_1 = datetime.datetime.now()
    ballot_for_queue_1 = Ballot.new(node_name_1, queue_message1, IsaacState.INIT, BallotVotingResult.agree, test_time_for_queue_1)
    ballot_for_queue_id_1 = ballot_for_queue_1.ballot_id

    # make queue 2
    queue_message2 = Message.new('Q_message2')
    test_time_for_queue_2 = datetime.datetime.now()
    ballot_for_queue_2 = Ballot.new(node_name_1, queue_message2, IsaacState.INIT, BallotVotingResult.agree, test_time_for_queue_2)
    ballot_for_queue_id_2 = ballot_for_queue_2.ballot_id

    # receive all ballot from client to bc1.
    bc1.receive_ballot(ballot_for_slot_11)
    bc1.receive_ballot(ballot_for_slot_21)
    bc1.receive_ballot(ballot_for_queue_1)
    bc1.receive_ballot(ballot_for_queue_2)

    # start consensus with ballot for slot 1
    index = bc1.consensus.slot.get_ballot_index(ballot_for_slot_11)
    bc1.receive_ballot(ballot_for_slot_12)
    bc1.receive_ballot(ballot_for_slot_13)

    bc2.receive_ballot(ballot_for_slot_11)
    bc2.receive_ballot(ballot_for_slot_12)
    bc2.receive_ballot(ballot_for_slot_13)

    bc3.receive_ballot(ballot_for_slot_11)
    bc3.receive_ballot(ballot_for_slot_12)
    bc3.receive_ballot(ballot_for_slot_13)

    # check slot is fully-occupied
    assert bc1.consensus.slot.slot[index].is_full is True
    # chceck queue is fully-occupied.
    ballot_from_queue = bc1.consensus.slot.slot_queue
    assert ballot_from_queue.full() is True
    assert node_name_1 in bc1.consensus.slot.slot[index].validator_ballots
    assert ballot_for_slot_11.ballot_id is bc1.consensus.slot.slot[index].validator_ballots[node_name_1].ballot_id

    assert bc1.consensus.slot.get_ballot_state(ballot_for_slot_11) is IsaacState.SIGN
    assert bc2.consensus.slot.get_ballot_state(ballot_for_slot_12) is IsaacState.SIGN
    assert bc3.consensus.slot.get_ballot_state(ballot_for_slot_13) is IsaacState.SIGN

    ballot_for_slot_11.state = IsaacState.SIGN
    ballot_for_slot_12.state = IsaacState.SIGN
    ballot_for_slot_13.state = IsaacState.SIGN

    bc1.receive_ballot(ballot_for_slot_11)
    bc1.receive_ballot(ballot_for_slot_12)
    bc1.receive_ballot(ballot_for_slot_13)

    bc2.receive_ballot(ballot_for_slot_11)
    bc2.receive_ballot(ballot_for_slot_12)
    bc2.receive_ballot(ballot_for_slot_13)

    bc3.receive_ballot(ballot_for_slot_11)
    bc3.receive_ballot(ballot_for_slot_12)
    bc3.receive_ballot(ballot_for_slot_13)

    assert bc1.consensus.slot.get_ballot_state(ballot_for_slot_11) is IsaacState.ACCEPT
    assert bc2.consensus.slot.get_ballot_state(ballot_for_slot_12) is IsaacState.ACCEPT
    assert bc3.consensus.slot.get_ballot_state(ballot_for_slot_13) is IsaacState.ACCEPT

    ballot_for_slot_11.state = IsaacState.ACCEPT
    ballot_for_slot_12.state = IsaacState.ACCEPT
    ballot_for_slot_13.state = IsaacState.ACCEPT

    bc1.receive_ballot(ballot_for_slot_11)
    bc1.receive_ballot(ballot_for_slot_12)
    bc1.receive_ballot(ballot_for_slot_13)

    bc2.receive_ballot(ballot_for_slot_11)
    bc2.receive_ballot(ballot_for_slot_12)
    bc2.receive_ballot(ballot_for_slot_13)

    bc3.receive_ballot(ballot_for_slot_11)
    bc3.receive_ballot(ballot_for_slot_12)
    bc3.receive_ballot(ballot_for_slot_13)

    assert message == bc1.consensus.messages.pop(0)
    assert message == bc2.consensus.messages.pop(0)
    assert message == bc3.consensus.messages.pop(0)

    # make consensus with ballot for slot 2
    index2 = bc1.consensus.slot.get_ballot_index(ballot_for_slot_21)
    bc1.receive_ballot(ballot_for_slot_22)
    bc1.receive_ballot(ballot_for_slot_23)

    bc2.receive_ballot(ballot_for_slot_21)
    bc2.receive_ballot(ballot_for_slot_22)
    bc2.receive_ballot(ballot_for_slot_23)

    bc3.receive_ballot(ballot_for_slot_21)
    bc3.receive_ballot(ballot_for_slot_22)
    bc3.receive_ballot(ballot_for_slot_23)

    # check slot is fully-occupied
    assert bc1.consensus.slot.slot[index2].is_full is True
    # chceck queue is fully-occupied.
    ballot_from_queue = bc1.consensus.slot.slot_queue
    assert ballot_from_queue.full() is False
    assert node_name_1 in bc1.consensus.slot.slot[index2].validator_ballots
    assert ballot_for_slot_21.ballot_id is bc1.consensus.slot.slot[index2].validator_ballots[node_name_1].ballot_id

    assert bc1.consensus.slot.get_ballot_state(ballot_for_slot_21) is IsaacState.SIGN
    assert bc2.consensus.slot.get_ballot_state(ballot_for_slot_22) is IsaacState.SIGN
    assert bc3.consensus.slot.get_ballot_state(ballot_for_slot_23) is IsaacState.SIGN

    ballot_for_slot_21.state = IsaacState.SIGN
    ballot_for_slot_22.state = IsaacState.SIGN
    ballot_for_slot_23.state = IsaacState.SIGN

    bc1.receive_ballot(ballot_for_slot_21)
    bc1.receive_ballot(ballot_for_slot_22)
    bc1.receive_ballot(ballot_for_slot_23)

    bc2.receive_ballot(ballot_for_slot_21)
    bc2.receive_ballot(ballot_for_slot_22)
    bc2.receive_ballot(ballot_for_slot_23)

    bc3.receive_ballot(ballot_for_slot_21)
    bc3.receive_ballot(ballot_for_slot_22)
    bc3.receive_ballot(ballot_for_slot_23)

    assert bc1.consensus.slot.get_ballot_state(ballot_for_slot_21) is IsaacState.ACCEPT
    assert bc2.consensus.slot.get_ballot_state(ballot_for_slot_22) is IsaacState.ACCEPT
    assert bc3.consensus.slot.get_ballot_state(ballot_for_slot_23) is IsaacState.ACCEPT

    ballot_for_slot_21.state = IsaacState.ACCEPT
    ballot_for_slot_22.state = IsaacState.ACCEPT
    ballot_for_slot_23.state = IsaacState.ACCEPT

    bc1.receive_ballot(ballot_for_slot_21)
    bc1.receive_ballot(ballot_for_slot_22)
    bc1.receive_ballot(ballot_for_slot_23)

    bc2.receive_ballot(ballot_for_slot_21)
    bc2.receive_ballot(ballot_for_slot_22)
    bc2.receive_ballot(ballot_for_slot_23)

    bc3.receive_ballot(ballot_for_slot_21)
    bc3.receive_ballot(ballot_for_slot_22)
    bc3.receive_ballot(ballot_for_slot_23)

    assert message2 == bc1.consensus.messages.pop(0)
    assert message2 == bc2.consensus.messages.pop(0)
    assert message2 == bc3.consensus.messages.pop(0)

    # Queue 1 make consensus.
    ballot_for_queue_11 = Ballot(ballot_for_queue_id_1, node_name_2, queue_message1, IsaacState.INIT, BallotVotingResult.agree, test_time_for_queue_1)
    ballot_for_queue_12 = Ballot(ballot_for_queue_id_1, node_name_3, queue_message1, IsaacState.INIT, BallotVotingResult.agree, test_time_for_queue_1)

    bc1.receive_ballot(ballot_for_queue_11)
    bc1.receive_ballot(ballot_for_queue_12)

    bc2.receive_ballot(ballot_for_queue_1)
    bc2.receive_ballot(ballot_for_queue_11)
    bc2.receive_ballot(ballot_for_queue_12)

    bc3.receive_ballot(ballot_for_queue_1)
    bc3.receive_ballot(ballot_for_queue_11)
    bc3.receive_ballot(ballot_for_queue_12)

    queue_index_1 = bc1.consensus.slot.get_ballot_index(ballot_for_queue_1)
    assert bc1.consensus.slot.slot[queue_index_1].is_full is True
    assert ballot_for_queue_1.ballot_id is bc1.consensus.slot.slot[queue_index_1].validator_ballots[node_name_1].ballot_id

    assert bc1.consensus.slot.get_ballot_state(ballot_for_queue_1) is IsaacState.SIGN
    assert bc2.consensus.slot.get_ballot_state(ballot_for_queue_11) is IsaacState.SIGN
    assert bc3.consensus.slot.get_ballot_state(ballot_for_queue_12) is IsaacState.SIGN

    ballot_for_queue_1.state = IsaacState.SIGN
    ballot_for_queue_11.state = IsaacState.SIGN
    ballot_for_queue_12.state = IsaacState.SIGN

    bc1.receive_ballot(ballot_for_queue_1)
    bc1.receive_ballot(ballot_for_queue_11)
    bc1.receive_ballot(ballot_for_queue_12)

    bc2.receive_ballot(ballot_for_queue_1)
    bc2.receive_ballot(ballot_for_queue_11)
    bc2.receive_ballot(ballot_for_queue_12)

    bc3.receive_ballot(ballot_for_queue_1)
    bc3.receive_ballot(ballot_for_queue_11)
    bc3.receive_ballot(ballot_for_queue_12)

    assert bc1.consensus.slot.get_ballot_state(ballot_for_queue_1) is IsaacState.ACCEPT
    assert bc2.consensus.slot.get_ballot_state(ballot_for_queue_11) is IsaacState.ACCEPT
    assert bc3.consensus.slot.get_ballot_state(ballot_for_queue_12) is IsaacState.ACCEPT

    ballot_for_queue_1.state = IsaacState.ACCEPT
    ballot_for_queue_11.state = IsaacState.ACCEPT
    ballot_for_queue_12.state = IsaacState.ACCEPT

    bc1.receive_ballot(ballot_for_queue_1)
    bc1.receive_ballot(ballot_for_queue_11)
    bc1.receive_ballot(ballot_for_queue_12)

    bc2.receive_ballot(ballot_for_queue_1)
    bc2.receive_ballot(ballot_for_queue_11)
    bc2.receive_ballot(ballot_for_queue_12)

    bc3.receive_ballot(ballot_for_queue_1)
    bc3.receive_ballot(ballot_for_queue_11)
    bc3.receive_ballot(ballot_for_queue_12)

    assert queue_message1 == bc1.consensus.messages.pop(0)
    assert queue_message1 == bc2.consensus.messages.pop(0)
    assert queue_message1 == bc3.consensus.messages.pop(0)

    # Queue 2 make consensus.
    ballot_for_queue_21 = Ballot(ballot_for_queue_id_2, node_name_2, queue_message2, IsaacState.INIT, BallotVotingResult.agree, test_time_for_queue_2)
    ballot_for_queue_22 = Ballot(ballot_for_queue_id_2, node_name_3, queue_message2, IsaacState.INIT, BallotVotingResult.agree, test_time_for_queue_2)

    bc1.receive_ballot(ballot_for_queue_21)
    bc1.receive_ballot(ballot_for_queue_22)

    bc2.receive_ballot(ballot_for_queue_2)
    bc2.receive_ballot(ballot_for_queue_21)
    bc2.receive_ballot(ballot_for_queue_22)

    bc3.receive_ballot(ballot_for_queue_2)
    bc3.receive_ballot(ballot_for_queue_21)
    bc3.receive_ballot(ballot_for_queue_22)

    assert bc1.consensus.slot.get_ballot_state(ballot_for_queue_2) is IsaacState.SIGN
    assert bc2.consensus.slot.get_ballot_state(ballot_for_queue_21) is IsaacState.SIGN
    assert bc3.consensus.slot.get_ballot_state(ballot_for_queue_22) is IsaacState.SIGN

    assert bc1.consensus.slot.slot_queue.empty() is True
    queue_index_2 = bc1.consensus.slot.get_ballot_index(ballot_for_queue_2)
    assert bc1.consensus.slot.slot[queue_index_2].is_full is True
    assert ballot_for_queue_2.ballot_id is bc1.consensus.slot.slot[queue_index_2].validator_ballots[node_name_1].ballot_id

    ballot_for_queue_2.state = IsaacState.SIGN
    ballot_for_queue_21.state = IsaacState.SIGN
    ballot_for_queue_22.state = IsaacState.SIGN

    bc1.receive_ballot(ballot_for_queue_2)
    bc1.receive_ballot(ballot_for_queue_21)
    bc1.receive_ballot(ballot_for_queue_22)

    bc2.receive_ballot(ballot_for_queue_2)
    bc2.receive_ballot(ballot_for_queue_21)
    bc2.receive_ballot(ballot_for_queue_22)

    bc3.receive_ballot(ballot_for_queue_2)
    bc3.receive_ballot(ballot_for_queue_21)
    bc3.receive_ballot(ballot_for_queue_22)

    assert bc1.consensus.slot.get_ballot_state(ballot_for_queue_2) is IsaacState.ACCEPT
    assert bc2.consensus.slot.get_ballot_state(ballot_for_queue_21) is IsaacState.ACCEPT
    assert bc3.consensus.slot.get_ballot_state(ballot_for_queue_22) is IsaacState.ACCEPT

    ballot_for_queue_2.state = IsaacState.ACCEPT
    ballot_for_queue_21.state = IsaacState.ACCEPT
    ballot_for_queue_22.state = IsaacState.ACCEPT

    bc1.receive_ballot(ballot_for_queue_2)
    bc1.receive_ballot(ballot_for_queue_21)
    bc1.receive_ballot(ballot_for_queue_22)

    bc2.receive_ballot(ballot_for_queue_2)
    bc2.receive_ballot(ballot_for_queue_21)
    bc2.receive_ballot(ballot_for_queue_22)

    bc3.receive_ballot(ballot_for_queue_2)
    bc3.receive_ballot(ballot_for_queue_21)
    bc3.receive_ballot(ballot_for_queue_22)

    assert queue_message2 == bc1.consensus.messages.pop(0)
    assert queue_message2 == bc2.consensus.messages.pop(0)
    assert queue_message2 == bc3.consensus.messages.pop(0)
