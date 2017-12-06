import logging
import json


log = logging.getLogger(__name__)


class Node:
    node_id = None
    url = None

    # @classmethod
    # def from_json(cls, s):
    #     d = json.loads(s)

    #     return cls(**d)

    def __init__(self, node_id, url):
        self.node_id = node_id
        self.url = url

    def to_json(self):
        return json.dumps(dict(
            node_id=self.node_id,
            url=self.url
        ))

    def __repr(self):
        return '<Node: %s(%s)>' % (self.node_id, self.url)

    def __eq__(self, rhs):
        rhs_url = rhs.url
        lhs_url = self.url

        t_str = '//localhost:'  # target_string
        r_str = '//127.0.0.1:'  # replace_string
        if t_str in rhs_url:
            rhs_url.replace(t_str, r_str)

        if t_str in lhs_url:
            lhs_url.replace(t_str, r_str)

        return lhs_url == rhs_url
