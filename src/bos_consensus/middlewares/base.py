import os.path
import pathlib

from ..util import get_module


def load_middlewares(module):
    middlewares = list()

    for i in pathlib.Path(__file__).parent.glob('*.py'):
        if i.name.startswith('.') or i.name.startswith('_'):
            continue
        if i.name in ('base.py'):
            continue

        name = os.path.splitext(i.name)[0]
        m = get_module('.' + name, package=('bos_consensus.middlewares.%s' % module))
        if m is None:
            continue

        middleware = getattr(m, 'Middleware', None)
        if middleware is None:
            continue

        middlewares.append(middleware)

    return middlewares
