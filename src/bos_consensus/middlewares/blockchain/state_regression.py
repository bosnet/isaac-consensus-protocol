from .base import BaseBlockchainMiddleware


class Middleware(BaseBlockchainMiddleware):
    def received_ballot(self, ballot):
        validator_ballots = list(map(
            lambda x: (x.node_name, x.state),
            self.blockchain.consensus.validator_ballots.values(),
        ))
        self.log.debug(
            'ballot received: %s -> %s validator_ballots=%s ballot=%s',
            ballot.node_name,
            self.blockchain.consensus.node.name,
            validator_ballots,
            ballot,
        )

        if ballot.node_name not in self.blockchain.consensus.validator_ballots:
            return

        existing = self.blockchain.consensus.validator_ballots[ballot.node_name]
        if existing is None:
            return

        if existing.state <= ballot.state:
            return

        self.log.debug('found state regression previous_ballot=%s received_ballot=%s', existing, ballot)

        return
