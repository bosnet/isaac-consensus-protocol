import copy

from .. import get_consensus_module
from ...ballot import Ballot
from ...message import Message
from ...node import Node


def copy_ballot(ballot, node_id, state):
    new_ballot = copy.copy(ballot)
    new_ballot.node_id = node_id
    if state is not None:
        new_ballot.node_state_kind = state

    return new_ballot


class SimpleTestNode(Node):
    validator_ballots = list()

    def __init__(self, *a, **kw):
        super(SimpleTestNode, self).__init__(*a, **kw)

        self.validator_ballots = list()

    def receive_ballots(self, *ballots):
        for ballot in ballots:
            self.receive_ballot(ballot)

        return


def test_same_message_after_allconfirm():
    node_id_1 = 'n1'
    node_id_2 = 'n2'
    node_id_3 = 'n3'

    consensus_module = get_consensus_module('simple_fba')
    node1 = SimpleTestNode(
        node_id_1,
        ('localhost', 5001),
        100,
        [node_id_2, node_id_3],
        consensus_module.Consensus(),
    )
    node1.init_node()

    StateKind = consensus_module.StateKind

    message = Message.new('message')

    ballot1 = Ballot.new(node_id_1, message, StateKind.INIT)
    ballot2 = copy_ballot(ballot1, node_id_2, StateKind.INIT)
    ballot3 = copy_ballot(ballot1, node_id_3, StateKind.INIT)

    node1.receive_ballots(ballot1, ballot2, ballot3)

    ballot1 = copy_ballot(ballot1, node_id_1, StateKind.SIGN)
    ballot2 = copy_ballot(ballot1, node_id_2, StateKind.SIGN)
    ballot3 = copy_ballot(ballot1, node_id_3, StateKind.SIGN)

    node1.receive_ballots(ballot1, ballot2, ballot3)

    assert len(node1.validator_ballots) > 0

    ballot1 = copy_ballot(ballot1, node_id_1, StateKind.ACCEPT)
    ballot2 = copy_ballot(ballot1, node_id_2, StateKind.ACCEPT)
    ballot3 = copy_ballot(ballot1, node_id_3, StateKind.ACCEPT)

    node1.receive_ballots(ballot1, ballot2, ballot3)

    assert node1.consensus.node_state.kind == StateKind.ALLCONFIRM

    # `Node.validator_ballots` will have same `ballot_id`
    assert list(set(map(lambda x: x.ballot_id, node1.validator_ballots.values()))) == [ballot1.ballot_id]

    # send same message in new ballot
    new_ballot1 = Ballot.new(node_id_1, message, StateKind.INIT)

    assert new_ballot1.ballot_id != ballot1.ballot_id

    ballot1 = copy_ballot(new_ballot1, node_id_1, StateKind.INIT)
    ballot2 = copy_ballot(new_ballot1, node_id_2, StateKind.INIT)
    ballot3 = copy_ballot(new_ballot1, node_id_3, StateKind.INIT)

    node1.receive_ballots(ballot1, ballot2, ballot3)

    # node state still remains the previous state
    assert node1.consensus.node_state.kind == StateKind.ALLCONFIRM

    assert len(list(filter(lambda x: x.ballot_id == ballot1.ballot_id, node1.validator_ballots.values()))) < 1

    return


def test_same_message_after_init():
    node_id_1 = 'n1'
    node_id_2 = 'n2'
    node_id_3 = 'n3'

    consensus_module = get_consensus_module('simple_fba')
    node1 = SimpleTestNode(
        node_id_1,
        ('localhost', 5001),
        100,
        [node_id_2, node_id_3],
        consensus_module.Consensus(),
    )
    node1.init_node()

    StateKind = consensus_module.StateKind

    message = Message.new('message')

    ballot1 = Ballot.new(node_id_1, message, StateKind.INIT)
    ballot2 = copy_ballot(ballot1, node_id_2, StateKind.INIT)
    ballot3 = copy_ballot(ballot1, node_id_3, StateKind.INIT)

    node1.receive_ballots(ballot1, ballot2, ballot3)

    assert node1.consensus.node_state.kind == StateKind.SIGN

    existing_ballot_ids = set(map(lambda x: x.ballot_id, node1.validator_ballots.values()))

    # send same message in new ballot, which has previous state
    new_ballot1 = Ballot.new(node_id_1, message, StateKind.INIT)

    assert new_ballot1.ballot_id != ballot1.ballot_id

    ballot1 = copy_ballot(new_ballot1, node_id_1, None)
    ballot2 = copy_ballot(new_ballot1, node_id_2, None)
    ballot3 = copy_ballot(new_ballot1, node_id_3, None)

    node1.receive_ballots(ballot1, ballot2, ballot3)

    # node state still remains the previous state
    assert node1.consensus.node_state.kind == StateKind.SIGN

    assert len(list(filter(lambda x: x.ballot_id == ballot1.ballot_id, node1.validator_ballots.values()))) < 1

    current_ballot_ids = set(map(lambda x: x.ballot_id, node1.validator_ballots.values()))

    assert existing_ballot_ids == current_ballot_ids

    return
