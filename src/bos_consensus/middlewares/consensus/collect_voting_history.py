from .base import BaseConsensusMiddleware
from bos_consensus.util import (
    datetime_to_timestamp,
    utcnow,
)


class Middleware(BaseConsensusMiddleware):
    def store(self, ballot):
        self.consensus.voting_histories.append(dict(
            received=datetime_to_timestamp(utcnow()),
            ballot_id=ballot.ballot_id,
            node=ballot.node_name,
            node_state=self.consensus.state,
            ballot_state=ballot.state,
            result=ballot.result,
        ))

        return
