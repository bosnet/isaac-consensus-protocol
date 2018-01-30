import os.path
import pathlib

from ..util import (
    get_module,
    LoggingMixin,
)


class NoFurtherMiddlewares(Exception):
    pass


class StopConsensus(Exception):
    pass


class BaseMiddleware(LoggingMixin):
    blockchain = None

    def __init__(self, blockchain):
        self.blockchain = blockchain

        super(BaseMiddleware, self).__init__()
        self.set_logging('middleware', node=self.blockchain.consensus.node.name)

    def received_ballot(self, ballot):
        pass

    def finished_ballot(self, ballot):
        pass


def load_middlewares():
    middlewares = list()

    for i in pathlib.Path(__file__).parent.glob('*.py'):
        if i.name.startswith('.') or i.name.startswith('_'):
            continue
        if i.name in ('base.py'):
            continue

        name = os.path.splitext(i.name)[0]
        m = get_module('.' + name, package='bos_consensus.middlewares')
        if m is None:
            continue

        middleware = getattr(m, 'Middleware', None)
        if middleware is None:
            continue

        middlewares.append(middleware)

    return middlewares
