from ...node import Node
from .. import get_consensus_module


def test_use_fake_consensus():
    simple_fba_consensus_module = get_consensus_module('simple_fba')
    simple_fba_consensus = simple_fba_consensus_module.Consensus()
    node = Node(1, ('localhost', 5001), 100, (), simple_fba_consensus)
    assert node.consensus.__module__.split('.')[-2] == 'simple_fba'

    fake_consensus_consensus_module = get_consensus_module('fake_consensus')
    fake_consensus_consensus = fake_consensus_consensus_module.Consensus()
    node = Node(1, ('localhost', 5001), 100, (), fake_consensus_consensus)

    assert node.consensus.__module__.split('.')[-2] == 'fake_consensus'
