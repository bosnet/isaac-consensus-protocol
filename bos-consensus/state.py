import logging

from ballot import Ballot

log = logging.getLogger(__name__)

class State:
    def handle_message(self, ballot):
        assert isinstance(ballot, Ballot)
        pass


class InitState(State):
    node = None

    def __init__(self, node):
        self.node = node

    def handle_message(self, ballot):
        print('[INIT]' + ballot)

    def __str__(self):
        return 'INIT'

class SignState(State):
    node = None

    def __init__(self, node):
        self.node = node

    def handle_message(self, ballot):
        assert isinstance(ballot, Ballot)
        print('[SIGN]' + ballot)

    def __str__(self):
        return 'SIGN'

class AcceptState(State):
    node = None

    def __init__(self, node):
        self.node = node

    def handle_message(self, ballot):
        assert isinstance(ballot, Ballot)
        print('[ACCEPT]' + ballot)

    def __str__(self):
        return 'ACCEPT'

class AllConfirmState(State):
    node = None

    def __init__(self, node):
        self.node = node

    def handle_message(self, ballot):
        assert isinstance(ballot, Ballot)
        print('[ALL_CONFIRM]' + ballot)

    def __str__(self):
        return 'ALL_CONFIRM'
