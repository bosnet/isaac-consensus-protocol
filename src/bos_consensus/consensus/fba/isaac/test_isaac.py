from bos_consensus.common.node import node_factory
from .isaac import IsaacConsensus


def test_isaac_consensus():
    node = node_factory('n1', ('http://localhost', 5001))
    consensus = IsaacConsensus(node, 100, ['http://localhost:5002', 'http://localhost:5003'])

    assert consensus.minimum == 3
    assert consensus.to_dict() == {
        'validator_endpoints': ['http://localhost:5002', 'http://localhost:5003'],
        'threshold': 100
    }
