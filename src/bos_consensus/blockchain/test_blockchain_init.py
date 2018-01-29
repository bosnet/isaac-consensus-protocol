from ..consensus import get_fba_module
from ..consensus.fba.isaac import IsaacState
from .util import StubTransport, blockchain_factory


IsaacConsensus = get_fba_module('isaac').IsaacConsensus


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
