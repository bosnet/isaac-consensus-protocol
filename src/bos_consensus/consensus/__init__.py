import importlib

from .base import BaseConsensus  # noqa


def get_consensus_module(name):
    try:
        return importlib.import_module('.' + name, package='bos_consensus.consensus')
    except ModuleNotFoundError:
        return None
