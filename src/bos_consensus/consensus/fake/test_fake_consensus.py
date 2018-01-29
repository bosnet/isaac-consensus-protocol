from bos_consensus.common import node_factory
from .fake import FakeConsensus


def test_use_fake():
    node = node_factory('n1', ('localhost', 5001))
    consensus = FakeConsensus(node)
    assert consensus.node_name == 'n1'
