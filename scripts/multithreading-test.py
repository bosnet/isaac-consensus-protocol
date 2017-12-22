import argparse
import collections
import colorlog
import configparser
import logging
import pathlib
import sys
import threading
import uuid

from bos_consensus.network import (
    BOSNetHTTPServer,
    BOSNetHTTPServerRequestHandler,
)
from bos_consensus.node import Node
from bos_consensus.util import get_local_ipaddress


logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
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

logging.root.handlers = [log_handler]

log = logging.getLogger(__name__)

parser = argparse.ArgumentParser()


class Options:

    def __init__(self, conf):
        self.conf = conf


def test_fba(options):
    config = collections.namedtuple(
        'Config',
        ('node_id', 'port', 'threshold', 'validators'),
    )(uuid.uuid1().hex, 8001, 51, [])

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
    log.debug('loaded conf: %s', config)

    validator_list = []
    for i in filter(lambda x: len(x.strip()) > 0, conf['node']['validator_list'].split(',')):
        validator_list.append(i.strip())

    config = config._replace(validators=validator_list)
    log.debug('Validators: %s' % config.validators)

    nd = Node(
        config.node_id,
        (get_local_ipaddress(), config.port),
        config.threshold,
        config.validators,
    )

    httpd = BOSNetHTTPServer(nd, ('0.0.0.0', config.port), BOSNetHTTPServerRequestHandler)

    httpd.serve_forever()


def make_conf(seq, num_validators, th_percent):
    id = str(5000 + seq)
    with open('examples/node' + id + '.ini', 'w') as f:
        f.write('[node]' + '\n')
        f.write('id=' + id + '\n')
        f.write('port=' + id + '\n')
        f.write('validator_list=')
        len_vlist = 0

        for i in range(1, num_validators + 1):
            if not i == seq:
                f.write('http://localhost:' + str(5000 + i))
                len_vlist += 1
                if len_vlist < num_validators - 1:
                    f.write(', ')

        f.write('\n')
        f.write('threshold_percent=' + th_percent + '\n')

    return 'examples/node' + id + '.ini'


if __name__ == '__main__':
    num_validators = int(sys.argv[1])
    th_percent = sys.argv[2]
    conf_list = []

    for i in range(1, num_validators + 1):
        conf_list.append(make_conf(i, num_validators, th_percent))

    if len(sys.argv) > 3:
        if sys.argv[3] == '-debug':
            logging.getLogger(__name__).root.setLevel(logging.DEBUG)
        elif sys.argv[3] == '-info':
            logging.getLogger(__name__).root.setLevel(logging.INFO)
    else:
        logging.getLogger(__name__).root.setLevel(logging.INFO)

    for c in conf_list:
        try:
            t_options = Options(c)
            t = threading.Thread(target=test_fba, args=(t_options,))
            t.start()
        except:  # noqa
            print('Error: unable to start thread')

    while 1:
        pass
