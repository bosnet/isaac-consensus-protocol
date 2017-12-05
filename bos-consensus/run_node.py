import requests
import urllib
import collections
import sys
import logging
import json
import colorlog
import configparser
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

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

if __name__ == '__main__':
	if len(sys.argv) != 2:
		error_message = "usage: " + __file__ + " input.ini "
		print(error_message)
		log.error(error_message)
		exit(2)
	input_ini_path = sys.argv[1].strip('"\'')
	ini_file = Path(input_ini_path)
	if not ini_file.is_file():
		error_message = 'File "' + input_ini_path + '" not exists!'
		print(error_message)
		log.error(error_message)
		exit(2)
	log.info('Ini file path: "' + input_ini_path + '"')
	conf.read(input_ini_path)
	id = conf['NODE']['ID']
	validators = conf['NODE']['VALIDATOR_LIST']
	print(id)
	print(validators)
