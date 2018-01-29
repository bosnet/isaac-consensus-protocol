import pprint  # noqa
import sys  # noqa
import threading
import time

from bos_consensus.consensus import get_fba_module
from bos_consensus.util import (
    datetime_to_timestamp,
    logger,
    utcnow,
)


CONSENSUS_MODULE = get_fba_module('isaac')

AUDITING_TIMEOUT = 5  # 5 seconds


class NoVotingAuditor(threading.Thread):
    checkpoint = None

    def __init__(self, blockchain):
        super(NoVotingAuditor, self).__init__()

        self.blockchain = blockchain
        self.checkpoint = 0

        self.log = logger.get_logger('audit.faulty-node.no-voting', node=self.blockchain.consensus.node.name)

    def _wait_for_connecting_validators(self):
        if not self.blockchain.consensus.all_validators_connected():
            return False

        self.validator_names = set(map(lambda x: x['node'].name, self.blockchain.consensus.validators.values()))
        self.validator_names.remove(self.blockchain.consensus.node.name)

        return True

    def run(self):
        '''
        # Auditing Rules

        1. wait for connecting all validators
        1. if ready, check received ballots
        1. if node(`node_state`) is not reached to the final state, ALLCONFIRM, keep watching
        1. if reached, collect the node to send ballot, which has the same `ballot_id`
        1. remember the `checkpoint`
        1. print log metric
        '''
        self.log.debug('waiting for connecting validators')
        while not self._wait_for_connecting_validators():
            time.sleep(2)

        self.log.debug('validators connected')

        while True:
            time.sleep(2)
            histories = self.blockchain.voting_histories[self.checkpoint:]
            if len(histories) < 1:
                continue

            # find the latest final state, `ALLCONFIRM`
            last_allconfirm = None
            for index in range(len(histories) - 1, -1, -1):
                history = histories[index]
                if history['node_state'] not in (CONSENSUS_MODULE.IsaacState.ALLCONFIRM,):
                    continue

                last_allconfirm = index
                break

            if last_allconfirm is None:
                continue

            last_allconfirm_history = histories[last_allconfirm]
            now = datetime_to_timestamp(utcnow())
            if now - last_allconfirm_history['received'] < AUDITING_TIMEOUT:
                continue

            prev_checkpoint = self.checkpoint
            self.checkpoint = len(self.blockchain.voting_histories)

            voted_nodes = set()
            for i in filter(lambda x: x['ballot_id'] == last_allconfirm_history['ballot_id'], histories):
                if i['node'] in voted_nodes:
                    continue

                voted_nodes.add(i['node'])

            self.log.metric(
                checkpoint=prev_checkpoint,
                validators=list(self.validator_names),
                voted_nodes=list(voted_nodes),
                no_voting_nodes=list(self.validator_names - voted_nodes),
            )

        return
