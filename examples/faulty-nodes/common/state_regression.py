import copy
import random

from bos_consensus.common import Ballot
from bos_consensus.consensus import get_fba_module
from bos_consensus.network import get_network_module
from bos_consensus.util import logger


CONSENSUS_MODULE = get_fba_module('isaac')

NETWORK_MODULE = get_network_module('default_http')


class StateRegressionTransport(NETWORK_MODULE.Transport):
    def __init__(self, faulty, **config):
        super(StateRegressionTransport, self).__init__(**config)

        assert hasattr(faulty, 'frequency')
        assert hasattr(faulty, 'target_nodes')
        assert type(faulty.target_nodes) in (list, tuple)

        self.faulty = faulty

    def start(self, blockchain, *a, **kw):
        self.log_faulty = logger.get_logger('transport.faulty', node=blockchain.consensus.node.name)

        return super(StateRegressionTransport, self).start(blockchain, *a, **kw)

    AVAILABLE_STATE = (
        CONSENSUS_MODULE.IsaacState.ACCEPT,
        CONSENSUS_MODULE.IsaacState.ALLCONFIRM,
    )

    def send(self, endpoint, data):
        if self.faulty.frequency == 0 or len(self.faulty.target_nodes) < 1:
            self.log_faulty.debug('not effective faulty: %s', self.faulty)

            return super(StateRegressionTransport, self).send(endpoint, data)

        if endpoint.get('name') not in self.faulty.target_nodes:
            self.log_faulty.debug('node, %s is not target for faulty: %s', endpoint.get('name'), self.faulty)

            return super(StateRegressionTransport, self).send(endpoint, data)

        if self.faulty.frequency != 100 and random.randint(0, 100) > self.faulty.frequency:
            self.log_faulty.debug('this ballot is under faulty, %s, but not this time', self.faulty)

            return super(StateRegressionTransport, self).send(endpoint, data)

        self.log_faulty.debug('this ballot is under faulty, %s', self.faulty)
        ballot = Ballot.from_dict(data)
        if ballot.state not in self.AVAILABLE_STATE:
            return super(StateRegressionTransport, self).send(endpoint, data)

        new_state = CONSENSUS_MODULE.IsaacState.get_from_value(
            random.randint(
                CONSENSUS_MODULE.IsaacState.INIT.value,
                ballot.state - 2,
            ),
        )

        new_ballot = copy.copy(ballot)
        new_ballot.state = new_state

        if not super(StateRegressionTransport, self).send(endpoint, ballot.serialize(to_string=False)):
            return False

        sent = super(StateRegressionTransport, self).send(endpoint, new_ballot.serialize(to_string=False))
        if not sent:
            return

        self.log_faulty.debug(
            'sent intentionally manipulated ballot=%s to=%s previous_ballot=%s',
            new_ballot,
            endpoint.get('name'),
            ballot,
        )

        return sent
