import logging


log = logging.getLogger(__name__)


class Ballot:
    ballot_num = None
    node_id = None
    message = None
    node_state = None

    def __init__(self, num, node_id, message, node_state = None):
        self.ballot_num = num
        self.node_id = node_id
        self.message = message
        self.node_state = node_state

    def __str__(self):
        return '%d:%d[%s]: %s' % (self.ballot_num, self.node_id, self.node_state, self.message)