import logging

from ballot import Ballot

log = logging.getLogger(__name__)


class State:
    def handle_ballot(self, ballot):
        assert isinstance(ballot, Ballot)
        pass


class InitState(State):
    node = None

    def __init__(self, node):
        self.node = node

    def handle_ballot(self, ballot):
        assert isinstance(ballot, Ballot)
        self.node.node_state = SignState(self.node)

    def __str__(self):
        return 'INIT'


class SignState(State):
    node = None

    def __init__(self, node):
        self.node = node

    def handle_ballot(self, ballot):
        assert isinstance(ballot, Ballot)
        ballots = self.node.get_validator_ballots()
        validator_th = self.node.get_validator_th()
        for node_id, node_ballot in ballots.items():
            assert isinstance(node_ballot, Ballot)
            if node_id == ballot.node_id:
                continue
            if isinstance(ballot.node_state, SignState) and ballot.message == node_ballot.message:
                validator_th -= 1

        if validator_th == 0:
            self.node.node_state = AcceptState(self.node)

        self.node.store(ballot)

    def __str__(self):
        return 'SIGN'


class AcceptState(State):
    node = None

    def __init__(self, node):
        self.node = node

    def handle_ballot(self, ballot):
        assert isinstance(ballot, Ballot)
        ballots = self.node.get_validator_ballots()
        validator_th = self.node.get_validator_th()
        for node_id, node_ballot in ballots.items():
            assert isinstance(node_ballot, Ballot)
            if node_id == ballot.node_id:
                continue
            if isinstance(ballot.node_state, AcceptState) and ballot.message == node_ballot.message:
                validator_th -= 1

        if validator_th == 0:
            self.node.node_state = AllConfirmState(self.node)

        self.node.store(ballot)

    def __str__(self):
        return 'ACCEPT'


class AllConfirmState(State):
    node = None

    def __init__(self, node):
        self.node = node

    def handle_ballot(self, ballot):
        assert isinstance(ballot, Ballot)
        pass

    def __str__(self):
        return 'ALL_CONFIRM'
