from ..util import get_module


def get_consensus_module(name):
    return get_module('.' + name, package='bos_consensus.consensus')


def get_fba_module(name):
    # without this, `SystemError: Parent module 'bos_consensus.consensus.fba'
    # not loaded, cannot perform relative import` occurred.
    get_consensus_module('fba')

    return get_module('.' + name, package='bos_consensus.consensus.fba')
