from ..network import BaseTransport
from ..blockchain import Blockchain
from ..consensus import get_fba_module
from ..common.node import node_factory


IsaacConsensus = get_fba_module('isaac').IsaacConsensus


class StubTransport(BaseTransport):
    def send(self, _, __):
        return


def blockchain_factory(name, address, threshold, validator_endpoints):
    node = node_factory(name, address)
    consensus = IsaacConsensus(node, threshold, validator_endpoints)
    return Blockchain(
        consensus,
        StubTransport()
    )
