from bos_consensus.common.node import node_factory
from bos_consensus.network import Endpoint

from .isaac import IsaacConsensus


def test_isaac_consensus():
    node = node_factory('n1', Endpoint.from_uri('http://localhost:5001'))

    validator_uris = ('http://localhost:5002', 'http://localhost:5003')
    validators = list()
    for uri in validator_uris:
        validators.append(
            node_factory(uri, Endpoint.from_uri(uri)),
        )

    consensus = IsaacConsensus(node, 100, validators)

    assert consensus.minimum == 3
    assert consensus.threshold == 100

    uris = list(map(lambda x: x.endpoint.uri, consensus.validator_candidates))
    assert set(validator_uris) == set(uris)
