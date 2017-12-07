import logging


log = logging.getLogger(__name__)


class Ballot:
    ballot_num = None
    message = None

    def __init__(self, num, message):
        self.ballot_num = num
        self.message = message

    def __str__(self):
        return '[%d]: %s' % (self.ballot_num, self.message)