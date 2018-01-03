import logging


log = logging.getLogger(__name__)


class Ballot:
    def __init__(self, num, node_id, message, node_state_kind):
        self.ballot_num = num
        self.node_id = node_id
        self.message = message
        self.node_state_kind = node_state_kind

    def __str__(self):
        return '%d:%d[%s]: %s' % (self.ballot_num, self.node_id, self.node_state_kind, self.message)

    def to_dict(self):
        return dict(
            ballot_num=self.ballot_num,
            node_id=self.node_id,
            message=self.message,
            node_state_kind=self.node_state_kind.name
        )
