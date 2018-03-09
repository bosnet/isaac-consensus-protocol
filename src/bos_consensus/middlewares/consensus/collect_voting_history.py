from .base import BaseConsensusMiddleware
from bos_consensus.util import (
    datetime_to_timestamp,
    utcnow,
)


class Middleware(BaseConsensusMiddleware):
    def handle_ballot(self, ballot):
        if self.consensus.slot.get_ballot_index(ballot) == 'Not Found':
            self.consensus.voting_histories.append(dict(
                received=datetime_to_timestamp(utcnow()),
                ballot_id=ballot.ballot_id,
                node=ballot.node_name,
                node_state='None',
                ballot_state=ballot.state,
                result=ballot.result,
            ))
        else:
            self.consensus.voting_histories.append(dict(
                received=datetime_to_timestamp(utcnow()),
                ballot_id=ballot.ballot_id,
                node=ballot.node_name,
                node_state=self.consensus.slot.slot[self.consensus.slot.get_ballot_index(ballot)].consensus_state,
                ballot_state=ballot.state,
                result=ballot.result,
            ))

        return
