from ..util import get_module


def get_consensus_module(name):
    return get_module('.' + name, package='bos_consensus.consensus')


def get_fba_module(name):
    return get_module('.' + name, package='bos_consensus.consensus.fba')
