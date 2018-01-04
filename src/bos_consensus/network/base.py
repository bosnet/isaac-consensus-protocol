import importlib

from ..node import Node


def get_network_module(name):
    try:
        return importlib.import_module('.' + name, package='bos_consensus.network')
    except ModuleNotFoundError:
        return None


class BaseNetwork:
    node = None
    config = None

    server = None

    def __init__(self, node, **config):
        assert isinstance(node, Node)

        self.node = node
        self.config = config

        self.server = None

    def start(self):
        self._start()

        return

    def _start(self):
        raise NotImplementedError

    def stop(self):
        if self.server is None:
            return

        self._stop()

        return

    def _stop(self):
        raise NotImplementedError
