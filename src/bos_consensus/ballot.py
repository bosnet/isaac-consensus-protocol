import logging


log = logging.getLogger(__name__)


class Ballot:
    def __init__(self, num, node_id, message, node_state_kind):
        self.ballot_num = num
        self.node_id = node_id
        self.message = message
        self.node_state_kind = node_state_kind

    def __repr__(self):
        return '<Ballot: ballot_num=%(ballot_num)d node_id=%(node_id)s node_state_kind=%(node_state_kind)s: %(message)s' % self.__dict__  # noqa

    def __eq__(self, a):
        return self.node_state_kind == a.node_state_kind and self.message == a.message  # noqa

    def to_dict(self):
        return dict(
            ballot_num=self.ballot_num,
            node_id=self.node_id,
            message=self.message,
            node_state_kind=self.node_state_kind.name
        )
