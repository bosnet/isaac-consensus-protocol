from ..common import Ballot, BallotVotingResult, Message
from ..blockchain.base import BaseBlockchain
from ..middlewares import (
    load_middlewares,
    NoFurtherBlockchainMiddlewares,
    StopReceiveBallot,
)


class Blockchain(BaseBlockchain):
    consensus = None
    middlewares = list()

    def __init__(self, consensus, transport=None):
        super(Blockchain, self).__init__(consensus.node, transport)
        self.consensus = consensus
        if transport:
            self.consensus.set_transport(transport)
        else:
            from ..network.default_http import Transport
            self.consensus.set_transport(Transport(bind=(
                '0.0.0.0',
                consensus.node.endpoint.port,
            )))

        self.middlewares = load_middlewares('blockchain')

    def get_state(self):
        return self.consensus.state

    def to_dict(self):
        return dict(
            node=self.node.to_dict(),
            consensus=self.consensus.to_dict(),
            state=self.consensus.state.name
        )

    def receive_message_from_client(self, message):
        assert isinstance(message, Message)

        self.log.metric(
            action='receive-message',
            messge=message.message_id,
            state=self.consensus.state.name,
        )
        ballot = Ballot.new(self.node_name, message, self.consensus.state, BallotVotingResult.agree)  # noqa
        self.receive_ballot(ballot)

        return

    def receive_ballot(self, ballot):
        '''
        Middleware for handling ballot
            1. each middleware execute before and after consensus
            1. if method of middleware returns,
                * `None`: pass
                * `NoFurtherBlockchainMiddlewares`: stop middlewares
                * `StopReceiveBallot`: stop consensus to handle ballot
            1. middleware keep the state in `receive_ballot`
        '''
        assert isinstance(ballot, Ballot)

        middlewares = list(map(lambda x: x(self), self.middlewares))

        for m in middlewares:
            try:
                m.received_ballot(ballot)
            except NoFurtherBlockchainMiddlewares as e:
                self.log.debug('break middleware: %s', e)
                break
            except StopReceiveBallot as e:
                self.log.debug('stop consensus: %s', e)
                return

        self.consensus.handle_ballot(ballot)

        for m in middlewares:
            try:
                m.finished_ballot(ballot)
            except NoFurtherBlockchainMiddlewares as e:
                self.log.debug('break middleware: %s', e)
                break

        return
