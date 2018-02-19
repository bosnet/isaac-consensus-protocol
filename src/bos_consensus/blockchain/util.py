from ..network import Endpoint, BaseTransport
from ..blockchain import Blockchain
from ..consensus import get_fba_module
from ..common import node_factory


IsaacConsensus = get_fba_module('isaac').IsaacConsensus


class StubTransport(BaseTransport):
    def __init__(self, *a, **kw):
        super(StubTransport, self).__init__(*a, **kw)

    def send(self, _, __):
        pass

    def set_requests(self):
        return


def blockchain_factory(name, address, threshold, validator_endpoint_uris):
    node = node_factory(name, Endpoint.from_uri(address))

    validators = list()
    for uri in validator_endpoint_uris:
        validators.append(
            node_factory(uri, Endpoint(uri, uri, 0)),
        )

    consensus = IsaacConsensus(node, threshold, validators)
    return Blockchain(
        consensus,
        StubTransport()
    )
