import argparse
import collections
import colorlog
import configparser
import logging
import pathlib
import uuid
import datetime

from bos_consensus.network import get_network_module, BaseServer
from bos_consensus.consensus import get_consensus_module
from bos_consensus.node import Node
from bos_consensus.node import Illnode
from bos_consensus.util import get_local_ipaddress

log_record_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s|%(filename)s:%(lineno)s] '
           '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

log_handler = colorlog.StreamHandler()
log_handler.setFormatter(
    colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
    ),
)

log = logging.getLogger(__name__)
logging.root.handlers = [log_handler]

parser = argparse.ArgumentParser()
parser.add_argument('-debug', action='store_true')
parser.add_argument('-info', action='store_true')
parser.add_argument('-log', action='store_true')
parser.add_argument('conf', help='ini config file for server node')


def main(options):
    config = collections.namedtuple(
        'Config',
        ('node_id', 'port', 'threshold', 'validators', 'bad_behavior_percent'),
    )(uuid.uuid1().hex, 8001, 51, [], 0)

    if not pathlib.Path(options.conf).exists():
        parser.error('conf file, `%s` does not exists.' % options.conf)

    if not pathlib.Path(options.conf).is_file():
        parser.error('conf file, `%s` is not valid file.' % options.conf)

    conf = configparser.ConfigParser()
    conf.read(options.conf)
    if parser.parse_args().log:
        log_file_handler = logging.FileHandler(
            'node_' + str(conf['node']['id']) + '_'
            + log_record_time + '_.log')
        logging.root.addHandler(log_file_handler)
    log.info('conf file, `%s` was loaded', options.conf)

    config = config._replace(node_id=conf['node']['id'])
    config = config._replace(port=int(conf['node']['port']))
    config = config._replace(threshold=int(conf['node']['threshold_percent']))

    if conf.has_option('bad', 'bad_behavior_percent'):
        config = config._replace(bad_behavior_percent=int(conf['bad']['bad_behavior_percent']))

    log.debug('loaded conf: %s', config)

    validator_list = []
    for i in filter(lambda x: len(x.strip()) > 0,
                    conf['node']['validator_list'].split(',')):
        validator_list.append(i.strip())

    config = config._replace(validators=validator_list)
    log.debug('Validators: %s' % config.validators)

    consensus_module = get_consensus_module('simple_fba')
    consensus = consensus_module.Consensus()

    if conf.has_option('bad', 'bad_behavior_percent'):
        nd = Illnode(
            config.node_id,
            (get_local_ipaddress(), config.port),
            config.threshold,
            config.validators,
            consensus,
            config.bad_behavior_percent,
        )
    else:
        nd = Node(
            config.node_id,
            (get_local_ipaddress(), config.port),
            config.threshold,
            config.validators,
            consensus,
        )

    network_module = get_network_module('default_http')
    transport = network_module.Transport(bind=('0.0.0.0', config.port))
    BaseServer(nd, transport).start()


if __name__ == '__main__':
    log_level = logging.ERROR

    options = parser.parse_args()
    if options.debug:
        log_level = logging.DEBUG
    if options.info:
        log_level = logging.INFO


    log.root.setLevel(log_level)

    log.debug('options: %s', options)
    main(options)
