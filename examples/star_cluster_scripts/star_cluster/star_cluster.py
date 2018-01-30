import collections
import configparser

from bos_consensus.common.node import Node
from bos_consensus.network import Endpoint


NodeInfo = collections.namedtuple(
    'NodeInfo',
    ['name', 'threshold', 'validators', 'ip', 'port', 'faulty_kind', 'faulty_percent'],
)


BASE_PORT = 5000


def push_node(nodes, node_info):
    assert isinstance(node_info, NodeInfo)
    if node_info.name not in nodes:
        nodes[node_info.name] = node_info


def set_nodes(nodes, name, node_infos, count):
    assert isinstance(node_infos, dict)

    new_node = NodeInfo(
        name,
        node_infos.get('threshold', 51),
        [],
        'http://localhost',
        BASE_PORT + count,
        node_infos.get('faulty_kind', ''),
        node_infos.get('faulty_percent', 0),
    )
    push_node(nodes, new_node)

    return


def get_node_name(node):
    if isinstance(node, str):
        return node
    else:
        raise EnvironmentError()


def link_each_other(nodes, from_list, to_list):
    link_from_to(nodes, from_list, to_list)
    link_from_to(nodes, to_list, from_list)


def link_from_to(nodes, from_list, to_list):
    for from_node in from_list:
        for to_node in to_list:
            from_node_name = get_node_name(from_node)
            to_node_name = get_node_name(to_node)
            if from_node_name == to_node_name:
                continue
            nodes[from_node_name].validators.append(to_node_name)


def organize_group(nodes, group_nodes_name):
    link_from_to(nodes, group_nodes_name, group_nodes_name)


def get_nodes(data):
    assert isinstance(data, dict)

    nodes = {}
    if 'nodes' in data:
        defined_nodes = data['nodes']
        for count, (node_name, node_infos) in enumerate(defined_nodes.items()):
            assert isinstance(node_infos, dict)
            set_nodes(nodes, node_name, node_infos, count)

    if 'groups' in data:
        groups = data['groups']
        for group_name, node_list in groups.items():
            assert isinstance(node_list, list)
            organize_group(nodes, node_list)

    if 'binary_link' in data:
        binary_links = data['binary_link']
        assert isinstance(binary_links, list)
        for binary_link in binary_links:
            assert isinstance(binary_link, list)
            assert len(binary_link) == 2
            from_list = binary_link[0]
            to_list = binary_link[1]
            link_each_other(nodes, from_list, to_list)

    if 'unary_link' in data:
        unary_links = data['unary_link']
        assert isinstance(unary_links, list)
        for unary_link in unary_links:
            assert isinstance(unary_link, list)
            assert len(unary_link) == 2
            from_list = unary_link[0]
            to_list = unary_link[1]
            link_from_to(nodes, from_list, to_list)

    set_validator_endpoint(nodes)
    return nodes


def print_to_ini_files(output_path, nodes):
    assert isinstance(output_path, str)
    assert isinstance(nodes, dict)

    config = configparser.ConfigParser()
    for name, node_info in nodes.items():
        assert isinstance(node_info, NodeInfo)
        config['node'] = {
            'id': node_info.id,
            'port': node_info.port,
            'threshold_percent': node_info.threshold,
            'validator_list': ', '.join(node_info.validators)
        }

        output_file_path = '%s/%s.ini' % (output_path, name)
        with open(output_file_path, 'w') as output_file:
            config.write(output_file)


def set_validator_endpoint(nodes):
    assert isinstance(nodes, dict)
    for name, node_info in nodes.items():
        assert isinstance(node_info, NodeInfo)
        validator_list = []
        for validator_name in node_info.validators:
            endpoint = Endpoint('http', nodes[validator_name].ip, nodes[validator_name].port)
            validator_list.append(Node(validator_name, endpoint))
        nodes[name] = nodes[name]._replace(validators=validator_list)
