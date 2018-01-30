import random

from bos_consensus.blockchain import Blockchain
from bos_consensus.consensus import get_fba_module
from bos_consensus.middlewares import (
    BaseMiddleware,
    StopConsensus,
)


class SometimesNoVotingBlockchain(Blockchain):
    faulty_frequency = None
    no_voting_ballot_ids = None  # store the ballot to be skipped

    def __init__(self, faulty_frequency, *a, **kw):
        super(SometimesNoVotingBlockchain, self).__init__(*a, **kw)

        self.middlewares.insert(0, SometimesNoVotingMiddleware)

        assert type(faulty_frequency) in (int,)
        assert faulty_frequency >= 0 and faulty_frequency <= 100

        self.faulty_frequency = faulty_frequency
        self.no_voting_ballot_ids = list()


class SometimesNoVotingMiddleware(BaseMiddleware):
    def received_ballot(self, ballot):
        consensus = self.blockchain.consensus
        if consensus.state in (consensus.get_init_state(),):
            if ballot.ballot_id not in self.blockchain.no_voting_ballot_ids and self.blockchain.faulty_frequency > 0:
                if self.blockchain.faulty_frequency == 100 or random.randint(0, 100) < self.blockchain.faulty_frequency:
                    self.log.info('[%s] no voting for ballot, %s in %s', consensus.node.name, ballot, consensus.state)
                    self.blockchain.no_voting_ballot_ids.append(ballot.ballot_id)

                    raise StopConsensus()

        if ballot.ballot_id in self.blockchain.no_voting_ballot_ids:
            self.log.info('[%s] no voting for ballot, %s in %s', consensus.node.name, ballot, consensus.state)

            raise StopConsensus()

        return
