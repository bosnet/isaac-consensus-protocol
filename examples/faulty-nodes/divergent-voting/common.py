import random

from bos_consensus.common import Ballot, BallotVotingResult
from bos_consensus.consensus import get_fba_module


IsaacConsensus = get_fba_module('isaac').Consensus


class DivergentVotingConsensus(IsaacConsensus):
    faulty_frequency = None
    faulty_ballot_ids = None  # store the ballot to be fault

    def __init__(self, faulty_frequency, *a, **kw):
        super(DivergentVotingConsensus, self).__init__(*a, **kw)

        assert type(faulty_frequency) in (int,)
        assert faulty_frequency >= 0 and faulty_frequency <= 100

        self.faulty_frequency = faulty_frequency
        self.faulty_ballot_ids = list()

    def make_self_ballot(self, ballot):
        if self.state in (self.get_init_state(),):
            if ballot.ballot_id not in self.faulty_ballot_ids and self.faulty_frequency > 0:
                if self.faulty_frequency > random.randint(0, 100):
                    self.log.info('[%s] divergent voting for ballot, %s in %s', self.node.name, ballot, self.state)
                    self.faulty_ballot_ids.append(ballot.ballot_id)

        result = ballot.result

        if ballot.ballot_id in self.faulty_ballot_ids:
            self.log.info('[%s] divergent voting for ballot, %s in %s', self.node.name, ballot, self.state)
            if ballot.result == BallotVotingResult.agree:
                result = BallotVotingResult.disagree
            else:
                result = BallotVotingResult.agree

        return Ballot(ballot.ballot_id, self.node_name, ballot.message, self.state, result)
