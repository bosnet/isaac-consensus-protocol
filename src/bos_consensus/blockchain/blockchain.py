from ..common.ballot import Ballot
from ..common.message import Message
from ..blockchain.base import BaseBlockchain
from ..network import BaseTransport
from ..network.default_http import Transport


class Blockchain(BaseBlockchain):
    consensus = None

    def __init__(self, consensus, transport=None):
        super(Blockchain, self).__init__(consensus.node)
        self.consensus = consensus
        if transport:
            self.consensus.set_transport(transport)
        else:
            self.consensus.set_transport(Transport(bind=('0.0.0.0', consensus.node.port)))

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
        assert isinstance(ballot, Ballot)
        self.consensus.handle_ballot(ballot)
