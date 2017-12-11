import logging
from statekind import StateKind


log = logging.getLogger(__name__)


class Ballot:
    def __init__(self, num, node_id, message, node_state=StateKind.INIT):
        self.ballot_num = num
        self.node_id = node_id
        self.message = message
        self.node_state = node_state

    def __str__(self):
        return '%d:%d[%s]: %s' % (self.ballot_num, self.node_id, self.node_state, self.message)
