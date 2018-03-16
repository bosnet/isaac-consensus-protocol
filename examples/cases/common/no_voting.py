import random

from bos_consensus.middlewares import (
    BaseBlockchainMiddleware,
    StopReceiveBallot,
)


class NoVotingMiddleware(BaseBlockchainMiddleware):
    faulty_frequency = None

    def __init__(self, *a, **kw):
        super(NoVotingMiddleware, self).__init__(*a, **kw)

    def received_ballot(self, ballot):
        try:
            return self._received_ballot(ballot)
        except StopReceiveBallot:
            self.log.metric(
                action='faulty-node',
                fault_type='no-voting',
                message=ballot.message.message_id,
                ballot=ballot.serialize(to_string=False),
            )
            raise

    def _received_ballot(self, ballot):
        if self.faulty_frequency == 0:
            return

        consensus = self.blockchain.consensus
        state = consensus.slot.get_ballot_state(ballot)
        if state in (consensus.get_init_state(),):
            if ballot.ballot_id not in self.blockchain.no_voting_ballot_ids and self.faulty_frequency > 0:
                if self.faulty_frequency == 100 or random.randint(0, 100) <= self.faulty_frequency:
                    self.log.info('[%s] no voting for ballot, %s in %s', consensus.node.name, ballot, state)
                    self.blockchain.no_voting_ballot_ids.append(ballot.ballot_id)

                    raise StopReceiveBallot()

        if ballot.ballot_id in self.blockchain.no_voting_ballot_ids:
            self.log.info('[%s] no voting for ballot, %s in %s', consensus.node.name, ballot, state)

            raise StopReceiveBallot()

        return
