from bos_consensus.common.ballot import Ballot
from bos_consensus.network import get_network_module


NETWORK_MODULE = get_network_module('default_http')


class StateRegressionTransport(NETWORK_MODULE.Transport):
    def __init__(self, faulty, **config):
        super(StateRegressionTransport, self).__init__(**config)

    def send(self, endpoint, data):
        ballot = Ballot.from_dict(data)

        return super(StateRegressionTransport, self).send(endpoint, ballot.serialize(to_string=False))
