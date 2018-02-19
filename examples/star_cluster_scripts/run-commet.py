import argparse
import json
import pathlib
import time

from client import send_message

from common import get_message_infos


parser = argparse.ArgumentParser()
parser.add_argument(
    '-i',
    '--input',
    required=True,
    help='Json format file that include client message configuration',
    type=str,
)


MS = 0.001


def main(options):
    input_file = options.input
    if not pathlib.Path(input_file).exists():
        parser.error('json file, `%s` does not exists.' % input_file)

    if not pathlib.Path(input_file).is_file():
        parser.error('json file, `%s` is not valid file.' % input_file)

    with open(input_file) as data_file:
        data = json.load(data_file)

    message_infos = get_message_infos(data)

    for message_info in message_infos:
        assert isinstance(message_info, tuple)
        message = message_info[0]
        interval = message_info[1]
        send_message(message)
        time.sleep(interval * MS)


if __name__ == '__main__':
    options = parser.parse_args()

    main(options)
