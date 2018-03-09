from .base import BaseBlockchainMiddleware


class Middleware(BaseBlockchainMiddleware):
    
    def received_ballot(self, ballot):

        validator_ballots = list(map(
            lambda x: (x.node_name, x.state),
            self.blockchain.consensus.slot.slot[self.blockchain.consensus.slot.get_ballot_index(ballot)].validator_ballots.values() ,
        )) if (self.blockchain.consensus.slot.get_ballot_index(ballot) != 'Not Found') else list()
        self.log.debug(
            'ballot received: %s -> %s validator_ballots=%s ballot=%s',
            ballot.node_name,
            self.blockchain.consensus.node.name,
            self.blockchain.consensus.slot.slot[self.blockchain.consensus.slot.get_ballot_index(ballot)].validator_ballots if (self.blockchain.consensus.slot.get_ballot_index(ballot) != 'Not Found') else 'None',
            ballot,
        )

        if self.blockchain.consensus.slot.get_ballot_index(ballot) != 'Not Found':
            if ballot.node_name not in self.blockchain.consensus.slot.slot[self.blockchain.consensus.slot.get_ballot_index(ballot)].validator_ballots:
                return

        if self.blockchain.consensus.slot.get_ballot_index(ballot) != 'Not Found':
            existing = self.blockchain.consensus.slot.slot[self.blockchain.consensus.slot.get_ballot_index(ballot)].validator_ballots[ballot.node_name]

            if existing is None:
                return

            if existing.state <= ballot.state:
                return

            self.log.debug('found state regression previous_ballot=%s received_ballot=%s', existing, ballot)

        return
