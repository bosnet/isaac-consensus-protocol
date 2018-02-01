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

    def __init__(self, consensus):
        super(DivergentAuditor, self).__init__()

        self.consensus = consensus
        self.checkpoint = 0

        self.log = logger.get_logger('audit.faulty-node.divergent-voting', node=self.consensus.node.name)

    def _wait_for_connecting_validators(self):
        if not self.consensus.all_validators_connected():
            return False

        self.validator_names = set(map(lambda x: x['node'].name, self.consensus.validators.values()))
        self.validator_names.remove(self.consensus.node.name)

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
            histories = self.consensus.voting_histories[self.checkpoint:]
            if len(histories) < 1:
                continue

            # find the latest final state, `ALLCONFIRM`
            last_allconfirm = None
            for index in range(len(histories) - 1, -1, -1):
                history = histories[index]
                if history['node_state'] not in (self.consensus.get_last_state(),):
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
            self.checkpoint = len(self.consensus.voting_histories)

            divergent = self.get_divergent_nodes(histories)

            self.log.metric(
                checkpoint=prev_checkpoint,
                validators=list(self.validator_names),
                divergent_voting_nodes=list(divergent),
            )
        return

    def get_ballot_dict(self, ballot_list):
        '''
        * make ballot dictionary from ballot_list
         * ballot dictionary format
          * {
              ballot_id: {
                  node_state: [ballots],
                  node_state: [ballots]
              },
              ballot_id: {
                  node_state: [ballots],
                  node_state: [ballots]
              }
          }
        '''
        ballot_dict = dict()

        for ballot in ballot_list:
            ballot_id = ballot['ballot_id']
            node_name = ballot['node']
            state = ballot['ballot_state']

            if ballot_id not in ballot_dict:
                ballot_dict[ballot_id] = dict()
            
            if state not in ballot_dict[ballot_id]:
                ballot_dict[ballot_id][state] = list()

            if node_name in self.validator_names or node_name == self.consensus.node_name:
                ballot_dict[ballot_id][state].append(ballot)
        return ballot_dict

    def remove_intersect_ballot(self, agree_list, disagree_list):
        intersect_set = agree_list & disagree_list
        if intersect_set:
            agree_list -= intersect_set
            disagree_list -= intersect_set

    def get_divergent_voting_nodes(self, ballot_list):
        agree_list = set(list())
        disagree_list = set(list())
        minimum = self.consensus.minimum
        for ballot in ballot_list:
            node_name = ballot['node']
            result = ballot['result']
            if result == BallotVotingResult.agree:
                agree_list.add(node_name)
            else:
                disagree_list.add(node_name)
        
        self.remove_intersect_ballot(agree_list, disagree_list)

        divergent = set(list())

        if len(agree_list) >= minimum and len(disagree_list) > 0:
            divergent.update(disagree_list)
        elif len(disagree_list) >= minimum and len(agree_list) > 0:
            divergent.update(agree_list)
        else:
            pass

        return divergent

    def get_divergent_nodes(self, histories):
        divergent = set(list())

        ballot_dict = self.get_ballot_dict(histories)

        for _, state_dict in ballot_dict.items():
            for _, ballot_list in state_dict.items():
                divergent_voting_nodes = self.get_divergent_voting_nodes(ballot_list)
                divergent.update(divergent_voting_nodes)

        return divergent
