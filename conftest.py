import sys
import logging
import pathlib


sys.path.insert(0, pathlib.Path('.').resolve() / 'src')


from bos_consensus.util import logger  # noqa


logger.set_level(logging.FATAL, 'http')
logging.getLogger('urllib3').setLevel(logging.FATAL)
