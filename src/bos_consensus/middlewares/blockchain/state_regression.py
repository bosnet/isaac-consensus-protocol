from .base import BaseBlockchainMiddleware
from bos_consensus.common import Slot


class Middleware(BaseBlockchainMiddleware):
    def received_ballot(self, ballot):
        ballot_idx = self.blockchain.consensus.slot.get_ballot_index(ballot)

        if ballot_idx == Slot.NOT_FOUND:
            validator_ballots = list()
        else:
            validator_ballots = self.blockchain.consensus.slot.slot[ballot_idx].validator_ballots

        self.log.debug(
            'ballot received: %s -> %s validator_ballots=%s ballot=%s',
            ballot.node_name,
            self.blockchain.consensus.node.name,
            validator_ballots,
            ballot,
        )

        if ballot.node_name not in validator_ballots:
            return

        existing = validator_ballots[ballot.node_name]

        if existing is None:
            return

        if existing.state <= ballot.state:
            return

        self.log.debug('found state regression previous_ballot=%s received_ballot=%s', existing, ballot)

        return
