from .. import get_consensus_module


simple_fba_module = get_consensus_module('simple_fba')


StateKind = simple_fba_module.StateKind


class Consensus(simple_fba_module.Consensus):
    pass
