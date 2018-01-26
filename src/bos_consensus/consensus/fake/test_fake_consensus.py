from bos_consensus.common.node import node_factory
from bos_consensus.network import Endpoint
from .fake import FakeConsensus


def test_use_fake():
    node = node_factory('n1', Endpoint.from_uri('http://localhost:5001'))
    consensus = FakeConsensus(node)
    assert consensus.node_name == 'n1'
