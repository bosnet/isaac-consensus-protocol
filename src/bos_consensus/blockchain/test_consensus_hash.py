from ..common import Ballot, BallotVotingResult, Message, node_factory
from ..network import Endpoint
from ..blockchain import Blockchain
from ..consensus import get_fba_module
from ..consensus.fba.isaac import IsaacState
from .util import StubTransport


IsaacConsensus = get_fba_module('isaac').IsaacConsensus


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


IsaacConsensus.transport = StubTransport()


def test_consensus_hash():
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

    bc1.consensus.add_to_validator_connected(bc2.node)
    bc1.consensus.add_to_validator_connected(bc3.node)
    bc1.consensus.init()

    validator_node_2 = bc1.consensus.validator_connected[node_name_2]
    validator_node_3 = bc1.consensus.validator_connected[node_name_3]

    assert hash(validator_node_2) == hash(bc2.consensus.node)
    assert hash(validator_node_3) == hash(bc3.consensus.node)
