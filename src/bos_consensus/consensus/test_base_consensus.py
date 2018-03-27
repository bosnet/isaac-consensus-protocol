from bos_consensus.network import Endpoint
from bos_consensus.consensus import get_fba_module
from bos_consensus.common import Message, Node


def test_base_consensus():
    node = Node('n1', Endpoint('http', 'localhost', 5001))
    consensus_module = get_fba_module('isaac')
    consensus = consensus_module.IsaacConsensus(
        node,
        100,
        tuple(),
    )

    assert hash(consensus) == 183908261690725173

    consensus.save_message(Message('id1', 'message1'))
    consensus.save_message(Message('id2', 'message2'))
    consensus.save_message(Message('id3', 'message3'))
    consensus.save_message(Message('id4', 'message4'))

    assert hash(consensus) == 1841909880308066977

    node2 = Node('n2', Endpoint('http', 'localhost', 5002))
    consensus_module = get_fba_module('isaac')
    consensus_2 = consensus_module.IsaacConsensus(
        node2,
        100,
        tuple(),
    )

    assert hash(consensus_2) == 183908261690725173

    consensus_2.save_message(Message('id1', 'message1'))
    consensus_2.save_message(Message('id2', 'message2'))
    consensus_2.save_message(Message('id3', 'message3'))
    consensus_2.save_message(Message('id4', 'message4'))

    assert hash(consensus_2) == 1841909880308066977
