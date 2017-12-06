import socket


def get_local_ipaddress():
    return socket.gethostbyname(socket.gethostname())
