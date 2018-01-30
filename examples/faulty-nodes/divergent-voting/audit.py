import threading
import time

from bos_consensus.consensus import get_fba_module
from bos_consensus.util import (
    datetime_to_timestamp,
    logger,
    utcnow,
)
from bos_consensus.common import BallotVotingResult


CONSENSUS_MODULE = get_fba_module('isaac')

AUDITING_TIMEOUT = 5  # 5 seconds


class DivergentAuditor(threading.Thread):
    checkpoint = None

    def __init__(self, blockchain):
        super(DivergentAuditor, self).__init__()

        self.blockchain = blockchain
        self.checkpoint = 0

        self.log = logger.get_logger('audit.faulty-node.divergent-voting', node=self.blockchain.consensus.node.name)

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
                if history['node_state'] not in (self.blockchain.consensus.get_last_state(),):
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

            normal, divergent = self.get_voting_nodes(histories)

            self.log.metric(
                checkpoint=prev_checkpoint,
                validators=list(self.validator_names),
                normal_voting_nodes=list(normal),
                divergent_voting_nodes=list(divergent),
            )
        return

    def get_voting_nodes(self, histories):
        normal = set(list())
        divergent = set(list())

        ballot_dict = dict()

        for ballot in histories:
            ballot_id = ballot['ballot_id']
            node_name = ballot['node']

            if ballot_id not in ballot_dict:
                ballot_dict[ballot_id] = list()

            if node_name in self.validator_names:
                ballot_dict[ballot_id].append(ballot)

        for _, ballot_list in ballot_dict.items():
            agree_list = set(list())
            disagree_list = set(list())
            for ballot in ballot_list:
                node_name = ballot['node']
                result = ballot['result']
                if result == BallotVotingResult.agree:
                    agree_list.add(node_name)
                else:
                    disagree_list.add(node_name)

            if len(agree_list) > 1 and len(disagree_list) == 1:
                normal.update(agree_list)
                divergent.update(disagree_list)
            elif len(agree_list) == 1 and len(disagree_list) > 1:
                normal.update(disagree_list)
                divergent.update(agree_list)
            elif len(disagree_list) == 0:
                normal.update(agree_list)
            elif len(agree_list) == 0:
                normal.update(disagree_list)

        return normal, divergent
