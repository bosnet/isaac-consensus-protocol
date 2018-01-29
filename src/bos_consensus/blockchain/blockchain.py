from ..common.ballot import Ballot
from ..common.message import Message
from ..blockchain.base import BaseBlockchain
from ..network import BaseTransport
from ..middlewares import (
    load_middlewares,
    NoFurtherMiddlewares,
    StopConsensus,
)


class Blockchain(BaseBlockchain):
    consensus = None
    middlewares = list()
    voting_histories = None  # for auditing received ballots

    def __init__(self, consensus, transport=None):
        super(Blockchain, self).__init__(consensus.node)
        self.consensus = consensus
        if transport:
            self.consensus.set_transport(transport)
        else:
            from ..network.default_http import Transport
            self.consensus.set_transport(Transport(bind=('0.0.0.0', consensus.node.port)))

        self.middlewares = load_middlewares()
        self.voting_histories = list()

    def set_transport(self, transport):
        assert isinstance(transport, BaseTransport)
        self.consensus.set_transport(transport)
        return

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

        ballot = Ballot.new(self.node_name, message, self.consensus.state)
        self.receive_ballot(ballot)

        return

    def receive_ballot(self, ballot):
        '''
        Middleware for handling ballot
            1. each middleware execute before and after consensus
            1. if method of middleware returns,
                * `None`: pass
                * `NoFurtherMiddlewares`: stop middlewares
                * `StopConsensus`: stop consensus to handle ballot
            1. middleware keep the state in `receive_ballot`
        '''
        assert isinstance(ballot, Ballot)

        middlewares = list(map(lambda x: x(self), self.middlewares))

        for m in middlewares:
            try:
                m.received_ballot(ballot)
            except NoFurtherMiddlewares as e:
                self.log.debug('break middleware: %s', e)
                break
            except StopConsensus as e:
                self.log.debug('stop consensus: %s', e)
                return

        self.consensus.handle_ballot(ballot)

        for m in middlewares:
            try:
                m.finished_ballot(ballot)
            except NoFurtherMiddlewares as e:
                self.log.debug('break middleware: %s', e)
                break

        return
