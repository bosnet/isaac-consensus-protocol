import socket
import logging


log = logging.getLogger(__name__)


def get_local_ipaddress():
    return socket.gethostbyname('localhost')
