import argparse
import collections
import json
import pathlib


NodeInfo = collections.namedtuple(
    'NodeInfo',
    ['name', 'threshold', 'validators'],
)

DEFAULT_THRESHOLD = 51


def push_node(nodes, name, node_info):
    if name not in nodes:
        nodes[name] = node_info


def set_nodes(nodes, node_list):
    for node_info in node_list:
        if isinstance(node_info, dict):
            for name, threshold in node_info.items():
                new_node = NodeInfo(name, threshold, [])
                push_node(nodes, name, new_node)
        elif isinstance(node_info, str):
            new_node = NodeInfo(node_info, DEFAULT_THRESHOLD, [])
            push_node(nodes, node_info, new_node)
    return


def get_node_name(node):
    if isinstance(node, str):
        return node
    elif isinstance(node, dict):
        assert len(node) == 1
        return list(node.keys())[0]
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


parser = argparse.ArgumentParser()
parser.add_argument(
    '-i',
    '--input',
    required=True,
    help='Json format file that include node and quorum informations',
    type=str,
)

parser.add_argument(
    '-o',
    '--output',
    required=True,
    help='Directory for output ini files',
    type=str,
)


def get_nodes(data):
    assert isinstance(data, dict)

    nodes = {}
    if 'groups' in data:
        groups = data['groups']
        for group_name, node_list in groups.items():
            assert isinstance(node_list, list)
            set_nodes(nodes, node_list)
            organize_group(nodes, node_list)

    if 'binary_link' in data:
        binary_links = data['binary_link']
        assert isinstance(binary_links, list)
        for binary_link in binary_links:
            assert isinstance(binary_link, list)
            assert len(binary_link) == 2
            from_list = binary_link[0]
            to_list = binary_link[1]
            set_nodes(nodes, from_list)
            set_nodes(nodes, to_list)
            link_each_other(nodes, from_list, to_list)

    if 'unary_link' in data:
        unary_links = data['unary_link']
        assert isinstance(unary_links, list)
        for unary_link in unary_links:
            assert isinstance(unary_link, list)
            assert len(unary_link) == 2
            from_list = unary_link[0]
            to_list = unary_link[1]
            set_nodes(nodes, from_list)
            set_nodes(nodes, to_list)
            link_from_to(nodes, from_list, to_list)

    return nodes


def main(options):
    input_file = options.input
    if not pathlib.Path(input_file).exists():
        parser.error('json file, `%s` does not exists.' % input_file)

    if not pathlib.Path(input_file).is_file():
        parser.error('json file, `%s` is not valid file.' % input_file)

    with open(input_file) as data_file:
        data = json.load(data_file)

    get_nodes(data)


if __name__ == '__main__':
    options = parser.parse_args()

    main(options)
