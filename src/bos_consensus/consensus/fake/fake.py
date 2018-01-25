from ...consensus.base import BaseConsensus


class FakeConsensus(BaseConsensus):
    def init(self):
        return

    def set_transport(self, transport):
        return
