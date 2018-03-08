import sys
import logging
import pathlib


sys.path.insert(0, str(pathlib.Path('.').resolve() / 'src'))


from bos_consensus.util import logger, LOG_LEVEL_METRIC  # noqa


logger.set_level(logging.FATAL, 'http')
logger.set_level(LOG_LEVEL_METRIC, 'consensus')
logging.getLogger('urllib3').setLevel(logging.FATAL)
