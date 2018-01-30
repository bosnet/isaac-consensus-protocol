from .base import BaseMiddleware
from ..util import (
    datetime_to_timestamp,
    utcnow,
)


class Middleware(BaseMiddleware):
    def received_ballot(self, ballot):
        self.blockchain.voting_histories.append(dict(
            received=datetime_to_timestamp(utcnow()),
            ballot_id=ballot.ballot_id,
            node=ballot.node_name,
            node_state=self.blockchain.get_state(),
            ballot_state=ballot.state,
            result=ballot.result,
        ))

        return
