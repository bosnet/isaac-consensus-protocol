import logging


log = logging.getLogger(__name__)


class Node:
    node_id = None
    address = None
    validators = None

    def __init__(self, node_id, address, validators):
        assert type(address) in (list, tuple) and len(address) == 2 and type(address[0]) in (str,) and type(address[1]) in (int,)

        self.node_id = node_id
        self.address = address
        self.validators = validators

    def __repr__(self):
        return '<Node: %s(%s)>' % (self.node_id, self.endpoint)

    @property
    def endpoint(self):
        return 'http://%s:%s' % self.address

    def to_dict(self):
        return dict(
            node_id=self.node_id,
            endpoint=self.endpoint,
            validators=self.validators,
        )

    def __eq__(self, rhs):
        rhs_endpoint = rhs.endpoint
        lhs_endpoint = self.endpoint

        t_str = '//localhost:'  # target_string
        r_str = '//127.0.0.1:'  # replace_string
        if t_str in rhs_endpoint:
            rhs_endpoint.replace(t_str, r_str)

        if t_str in lhs_endpoint:
            lhs_endpoint.replace(t_str, r_str)

        return lhs_endpoint == rhs_endpoint
