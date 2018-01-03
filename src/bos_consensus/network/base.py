import importlib


def get_network_module(name):
    try:
        return importlib.import_module('.' + name, package='bos_consensus.network')
    except ModuleNotFoundError:
        return None


class BaseNetwork:
    def __init__(self):
        pass
