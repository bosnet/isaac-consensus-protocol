import argparse
import json
import pathlib
import time

from client.client import (
    MessageInfo,
    send_message
)


parser = argparse.ArgumentParser()
parser.add_argument(
    '-i',
    '--input',
    required=True,
    help='Json format file that include client message configuration',
    type=str,
)


def get_message_infos(message_data):
    assert isinstance(message_data, dict)
    message_infos = []

    for node_name, node_infos in message_data.items():
        assert isinstance(node_infos, dict)
        assert 'ip' in node_infos
        assert 'port' in node_infos

        ip = node_infos['ip']
        port = node_infos['port']

        if 'message' in node_infos:
            message_list = node_infos['message']
            assert isinstance(message_list, list)
            for message in message_list:
                assert isinstance(message, str)
                new_message = MessageInfo(ip, port, message)
                message_infos.append(new_message)

        if 'bulk_message' in node_infos:
            bulk_message_dict = node_infos['bulk_message']
            assert isinstance(bulk_message_dict, dict)
            assert 'number' in bulk_message_dict
            assert 'message_format' in bulk_message_dict

            message_count = bulk_message_dict['number']
            message_format = bulk_message_dict['message_format']

            for i in range(0, message_count):
                message = message_format % i
                new_message = MessageInfo(ip, port, message)
                message_infos.append(new_message)

    return message_infos


MS = 0.001


def main(options):
    input_file = options.input
    if not pathlib.Path(input_file).exists():
        parser.error('json file, `%s` does not exists.' % input_file)

    if not pathlib.Path(input_file).is_file():
        parser.error('json file, `%s` is not valid file.' % input_file)

    with open(input_file) as data_file:
        data = json.load(data_file)

    assert 'messages' in data

    interval = 1000
    if 'interval' in data:
        interval = data['interval']

    message_infos = get_message_infos(data['messages'])

    for message_info in message_infos:
        assert isinstance(message_info, MessageInfo)
        send_message(message_info)
        time.sleep(interval * MS)


if __name__ == '__main__':
    options = parser.parse_args()

    main(options)
