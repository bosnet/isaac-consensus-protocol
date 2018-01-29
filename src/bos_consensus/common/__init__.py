from .node import Node
from .faulty_node import FaultyNode


def node_factory(name, address, faulty_kind_str=None, faulty_percent=0):
    assert type(address) in (list, tuple) and len(address) == 2
    assert type(address[0]) in (str,) and type(address[1]) in (int,)
    endpoint = 'http://%s:%s?name=%s' % (address[0], address[1], name)
    if faulty_kind_str is None or faulty_percent == 0:
        return Node(name, endpoint)
    else:
        return FaultyNode(name, endpoint, faulty_kind_str, faulty_percent)
