def get_message_infos(data):
    interval = 1000
    if 'interval' in data:
        interval = data['interval']

    assert 'messages' in data

    message_infos = []

    for node_name, node_info_list in data['messages'].items():
        assert isinstance(node_info_list, dict)

        number = node_info_list.get('number', 1)
        message_format = node_info_list.get('message_format', 'default_message_%d')
        interval = node_info_list.get('interval', 4000)

        for i in range(0, number):
            new_message = message_format % i
            message_infos.append((new_message, interval))

    return message_infos
