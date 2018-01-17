import argparse
import collections
import configparser
import pathlib
import uuid

from bos_consensus.consensus import get_consensus_module
from bos_consensus.network import get_network_module, BaseServer
from bos_consensus.node import Illnode
from bos_consensus.node import Node
from bos_consensus.util import get_local_ipaddress, logger


parser = argparse.ArgumentParser()
parser.add_argument('conf', help='ini config file for server node')

log = None

logger.set_argparse(parser)


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

    log.metric(node=nd.node_id, data=nd.to_dict())

    network_module = get_network_module('default_http')
    transport = network_module.Transport(bind=('0.0.0.0', config.port))
    server = BaseServer(nd, transport)
    server.start()

    return


if __name__ == '__main__':
    options = parser.parse_args()
    logger.from_argparse(logger, options)

    log = logger.get_logger(__name__)

    log.debug('options: %s', options)
    log.debug('log settings: %s', logger.info)

    main(options)
