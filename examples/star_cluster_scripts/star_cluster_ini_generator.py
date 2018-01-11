import argparse
import collections
import configparser
import json
import pathlib
import os


from star_cluster.star_cluster import (
    get_nodes,
    NodeInfo,
    print_to_ini_files
)


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


def main(options):
    input_path = options.input
    if not pathlib.Path(input_path).exists():
        parser.error('json file, `%s` does not exists.' % input_path)

    if not pathlib.Path(input_path).is_file():
        parser.error('json file, `%s` is not valid file.' % input_path)

    with open(input_path) as input_data:
        data = json.load(input_data)

    nodes = get_nodes(data)

    output_path = options.output
    if not pathlib.Path(output_path).exists():
        os.mkdir(output_path)
    print_to_ini_files(output_path, nodes)


if __name__ == '__main__':
    options = parser.parse_args()

    main(options)
