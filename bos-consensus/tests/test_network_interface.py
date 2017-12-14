from node import Node
from network import (
    BOSNetHTTPServer,
    BOSNetHTTPServerRequestHandler,
)
import requests
import threading
import urllib


def test_sample():
    print('test_sample')
    assert 1 == 1


# class Server(threading.Thread):
#     def __init__(self):
#         super(Server, self).__init__()

#     def run(self):
#         node = Node(1, ('localhost', 5001), 100, ['localhost:5002', 'localhost:5003'])
#         httpd = BOSNetHTTPServer(node, ('localhost', 5001), BOSNetHTTPServerRequestHandler)
#         httpd.serve_forever()
#         return True

# def test_handler_ping():
#     print('test_handler_ping Start!')
#     t = Server()
#     print('Server implement!')
#     t.start()
#     print('Thread Start!')
#     t.join()

#     try:
#         response = requests.get(
#             urllib.parse.urljoin('http://localhost:5001', '/ping')
#             )
#         assert response.status_code == 200
#         t.join()
#     except requests.exceptions.ConnectionError:
#         print('Connection Refused!')
#         t.join()
