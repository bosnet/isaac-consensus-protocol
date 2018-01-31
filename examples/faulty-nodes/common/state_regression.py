import copy

from bos_consensus.common.ballot import Ballot
from bos_consensus.consensus import get_fba_module
from bos_consensus.network import get_network_module


CONSENSUS_MODULE = get_fba_module('isaac')

NETWORK_MODULE = get_network_module('default_http')


class StateRegressionTransport(NETWORK_MODULE.Transport):
    def __init__(self, faulty, **config):
        super(StateRegressionTransport, self).__init__(**config)

        assert hasattr(faulty, 'frequency')
        assert hasattr(faulty, 'target_nodes')
        assert type(faulty.target_nodes) in (list, tuple)

        self.faulty = faulty

    AVAILABLE_STATE = (
        # CONSENSUS_MODULE.IsaacState.SIGN,
        CONSENSUS_MODULE.IsaacState.ACCEPT,
        CONSENSUS_MODULE.IsaacState.ALLCONFIRM,
    )

    def send(self, endpoint, data):
        if endpoint.get('name') not in self.faulty.target_nodes:
            return super(StateRegressionTransport, self).send(endpoint, data)

        ballot = Ballot.from_dict(data)
        if ballot.state not in self.AVAILABLE_STATE:
            return super(StateRegressionTransport, self).send(endpoint, data)

        new_state = CONSENSUS_MODULE.IsaacState.get_from_value(ballot.state - 2)

        new_ballot = copy.copy(ballot)
        new_ballot.state = new_state

        if not super(StateRegressionTransport, self).send(endpoint, ballot.serialize(to_string=False)):
            return False

        sent = super(StateRegressionTransport, self).send(endpoint, new_ballot.serialize(to_string=False))
        if not sent:
            return

        self.log.debug(
            'sent intentionally manipulated ballot=%s to=%s previous_ballot=%s',
            new_ballot,
            endpoint.get('name'),
            ballot,
        )

        return sent
