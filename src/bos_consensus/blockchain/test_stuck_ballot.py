import copy
import threading
import time

from bos_consensus.common import Ballot, BallotVotingResult, Message, node_factory
from bos_consensus.consensus import get_fba_module
from bos_consensus.network import Endpoint
from .blockchain import Blockchain
from .util import StubTransport

LIMIT_TIME = 0.1


def copy_ballot(ballot, node_name, state):
    new_ballot = copy.copy(ballot)
    new_ballot.node_name = node_name
    if state is not None:
        new_ballot.state = state

    return new_ballot


def stub(self, ballot):
    timer = threading.Timer(LIMIT_TIME, self._remove_stuck_ballot, args=[ballot])
    timer.start()


Consensus = get_fba_module('isaac').Consensus
Consensus._check_slot_time = stub
IsaacState = get_fba_module('isaac').State


class SimpleBlockchain(Blockchain):
    def __init__(self, *a, **kw):
        super(SimpleBlockchain, self).__init__(*a, **kw)

    def receive_ballots(self, *ballots):
        for ballot in ballots:
            self.receive_ballot(ballot)

        return


def simple_blockchain_factory(name, address, threshold, validator_endpoint_uris):
    node = node_factory(name, Endpoint.from_uri(address))

    validators = list()
    for uri in validator_endpoint_uris:
        validators.append(
            node_factory(uri, Endpoint(uri, uri, 0)),
        )

    consensus = Consensus(node, threshold, validators)

    transport = StubTransport(bind=('0.0.0.0', 5001))

    return SimpleBlockchain(consensus, transport)


def test_confirm_stuck_ballot():
    node_name_1 = 'http://localhost:5001'
    node_name_2 = 'http://localhost:5002'
    node_name_3 = 'http://localhost:5003'

    bc1 = simple_blockchain_factory(
        node_name_1,
        'http://localhost:5001',
        100,
        [node_name_2, node_name_3],
    )

    node2 = node_factory(node_name_2, Endpoint.from_uri('http://localhost:5002'))
    node3 = node_factory(node_name_3, Endpoint.from_uri('http://localhost:5003'))

    bc1.consensus.add_to_validator_connected(node2)
    bc1.consensus.add_to_validator_connected(node3)

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

    assert bc1.consensus.slot.get_ballot_state(ballot_init_1) == IsaacState.SIGN

    time.sleep(LIMIT_TIME + 0.1)

    assert bc1.consensus.slot.get_ballot_state(ballot_init_1) == IsaacState.NONE

    return
