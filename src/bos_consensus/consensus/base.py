from ..util import LoggingMixin


class BaseConsensus(LoggingMixin):
    node = None
    messages = None
    message_ids = None

    def __init__(self, node):
        super(BaseConsensus, self).__init__()
        self.node = node
        self.set_logging('consensus', node=self.node.name)
        self.messages = list()
        self.message_ids = list()

    def init(self):
        raise NotImplementedError()

    def set_transport(self, transport):
        raise NotImplementedError()

    @property
    def node_name(self):
        return self.node.name

    def save_message(self, message):
        self.messages.append(message)
        self.message_ids.append(message.message_id)
