import collections
import sys
import logging
import json
import uuid
import colorlog
from urllib.parse import urlparse
import configparser
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

import handler


conf = configparser.ConfigParser()
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


class BosNetHTTPServer(HTTPServer):
    id = None
    validators = None

    def __init__(self, id, validators, *a, **kw):
        super(BosNetHTTPServer, self).__init__(*a, **kw)

        self.id = id
        self.validators = validators

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(self.id, self.validators, request, client_address, self)

        return


class BosNetHTTPServer_RequestHandler(BaseHTTPRequestHandler):
    id = None
    validators = None

    def __init__(self, id, validators, *a, **kw):
        super(BosNetHTTPServer_RequestHandler, self).__init__(*a, **kw)

        self.id = id
        self.validators = validators

    def do_GET(self):
        log.debug('> start request: %s', self.path)
        parsed = urlparse(self.path)
        func = handler.HTTP_HANDLERS.get(parsed.path[1:].split('/')[0], handler.not_found_handler)
        r = func(self, parsed)

        log.debug('< finished request: %s', self.path)
        return r

    do_POST = do_GET

    def response(self, status_code, message, **headers):
        self.send_response(status_code)
        for k, v in headers.items():
            self.send_header(k, v)

        self.end_headers()

        if message is not None:
            self.wfile.write(bytes(message + ('\n' if message[-1] != '\n' else ''), "utf8"))

        return

    def json_response(self, status_code, message, **headers):
        if type(message) not in (str,):
            message = json.dumps(message)

        headers['Content-Type'] = 'application/json'

        return self.response(status_code, message, **headers)


if __name__ == '__main__':
    options = collections.namedtuple(
        'Options',
        ('id', 'port', 'validators'),
    )(uuid.uuid1().hex, 8001, [])

    if len(sys.argv) != 2:
        error_message = 'usage: ' + __file__ + ' conf.ini '
        print(error_message)
        log.error(error_message)
        exit(2)
    input_ini_path = sys.argv[1].strip('"\'')
    if not Path(input_ini_path).is_file():
        error_message = 'File "' + input_ini_path + '" not exists!'
        print(error_message)
        log.error(error_message)
        exit(2)
    log.info('Ini file path: "' + input_ini_path + '"')
    log.root.setLevel(logging.DEBUG)
    conf.read(input_ini_path)
    options = options._replace(id=conf['NODE']['ID'])
    log.debug('Node ID: %s' % options.id)

    options = options._replace(port=int(conf['NODE']['PORT']))
    log.debug('Node PORT: %s' % options.port)

    validator_list = []
    for i in filter(lambda x: len(x.strip()) > 0, conf['NODE']['VALIDATOR_LIST'].split(',')):
        validator_list.append(i.strip())
    options = options._replace(validators=validator_list)
    log.debug('Validators: %s' % options.validators)

    node_address = ('0.0.0.0', options.port)
    httpd = BosNetHTTPServer(
        options.id,
        options.validators,
        node_address,
        BosNetHTTPServer_RequestHandler,
    )

    httpd.serve_forever()
