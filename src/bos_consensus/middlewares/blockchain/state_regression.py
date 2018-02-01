from .base import BaseBlockchainMiddleware


class Middleware(BaseBlockchainMiddleware):
    def received_ballot(self, ballot):
        validator_ballots = list(map(
            lambda x: (x['node'].name, x['ballot'].state if x['ballot'] else ''),
            self.blockchain.consensus.validators.values(),
        ))
        self.log.debug(
            'ballot received: %s -> %s validator_ballots=%s ballot=%s',
            ballot.node_name,
            self.blockchain.consensus.node.name,
            validator_ballots,
            ballot,
        )

        if ballot.node_name not in self.blockchain.consensus.validators:
            return

        existing = self.blockchain.consensus.validators[ballot.node_name]['ballot']
        if existing is None:
            return

        if existing.state <= ballot.state:
            return

        self.log.debug('found state regression previous_ballot=%s received_ballot=%s', existing, ballot)

        return
