import asyncio

from bos_consensus.util import (
    datetime_to_timestamp,
    logger,
    utcnow,
)

from bos_consensus.common import BallotVotingResult


INFINITE = -1
INIT = -1
MS = 0.001


class BaseAuditor:
    checkpoint = None
    loop = None
    time_limit = None
    waiting = None
    validator_names = None
    log = None

    def __init__(self, blockchain, loop, waiting=3000, time_limit=INFINITE):
        self.consensus = blockchain.consensus
        self.loop = loop
        self.checkpoint = INIT
        self.waiting = waiting * MS
        self.time_limit = time_limit * MS
        self.validator_names = set(map(lambda x: x.name, self.consensus.validator_candidates))
        self.log = logger.get_logger(self._log_name(), node=self.consensus.node.name)

    def _log_name(self):
        raise NotImplementedError()

    def _wait_for_connecting_validators(self):
        if not self.consensus.all_validators_connected():
            return False

        return True

    def _log_metric(self, prev_checkpoint, history):
        raise NotImplementedError()

    def get_last_voting_idx(self, histories):
        last_voting_idx = None
        last_voting_idx = self.get_last_ballot_idx(histories)

        if last_voting_idx is None:
            last_voting_idx = self.get_last_allconfirm(histories)

        return last_voting_idx

    def get_last_ballot_idx(self, histories):
        '''
        find the last ballot before next ballot
        '''
        last_ballot_idx = None
        prev_ballot_id = histories[0]['ballot_id']
        for index in range(self.checkpoint + 1, len(histories)):
            history = histories[index]
            if prev_ballot_id == history['ballot_id']:
                continue

            last_ballot_idx = index - 1
            break

        return last_ballot_idx

    def get_last_allconfirm(self, histories):
        '''
        find the latest final state, `ALLCONFIRM`
        '''
        last_allconfirm = None
        for index in range(len(histories) - 1, -1, -1):
            history = histories[index]
            if history['node_state'] not in (self.consensus.get_last_state(),):
                continue

            last_allconfirm = index
            break

        return last_allconfirm

    async def coroutine(self):
        '''
        # Auditing Rules

        1. wait for connecting all validators
        1. if ready, check received ballots
        1. if node(`node_state`) did not receive next ballot, keep watching
        1. if received, collect the node to send ballot, which has the same `ballot_id`
        1. remember the `checkpoint`
        1. print log metric
        '''

        self.log.debug('waiting for connecting validators')
        while not self._wait_for_connecting_validators():
            await asyncio.sleep(1)

        self.log.debug('started to audit; validators connected')

        last_check_time = datetime_to_timestamp(utcnow())

        while True:
            await asyncio.sleep(1)
            histories = self.consensus.voting_histories[self.checkpoint:]
            now = datetime_to_timestamp(utcnow())

            if self.is_audit_reached_time_limit(last_check_time, now):
                return

            if len(histories) < 1:
                continue

            last_voting_idx = self.get_last_voting_idx(histories)
            if last_voting_idx is None:
                continue

            last_voting_history = histories[last_voting_idx]
            last_received_time = last_voting_history['received']

            if now - last_received_time < self.waiting:
                continue

            last_check_time = now
            prev_checkpoint = self.checkpoint
            self.checkpoint = len(self.consensus.voting_histories)

            collected_history = filter(lambda x: x['ballot_id'] == last_voting_history['ballot_id'], histories)
            self._log_metric(prev_checkpoint, collected_history)

        return

    def is_audit_reached_time_limit(self, last_check_time, now):
        if self.time_limit == INFINITE:
            return False
        return now - last_check_time > self.time_limit


class LivenessAuditor(BaseAuditor):
    def _log_name(self):
        return 'health-check.liveness'

    def _log_metric(self, prev_checkpoint, history):
        if not self.consensus.is_guarantee_liveness():
            self.log.metric(
                liveness='Failed',
                minimum=self.consensus.minimum,
                validators=list(self.consensus.validator_connected),
                faulties=self.consensus.validator_faulty,
            )


class DivergentAuditor(BaseAuditor):
    def _log_name(self):
        return 'faulty-node.divergent-voting'

    def _log_metric(self, prev_checkpoint, history):
        divergent = self.get_divergent_nodes(history)

        self.log.metric(
            checkpoint=prev_checkpoint,
            validators=list(self.validator_names),
            divergent_voting_nodes=list(divergent),
        )

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
              },
              ...
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
        agree_list = set()
        disagree_list = set()
        minimum = self.consensus.minimum
        for ballot in ballot_list:
            node_name = ballot['node']
            result = ballot['result']
            if result == BallotVotingResult.agree:
                agree_list.add(node_name)
            else:
                disagree_list.add(node_name)

        self.remove_intersect_ballot(agree_list, disagree_list)

        divergent = set()

        if len(agree_list) >= minimum and len(disagree_list) > 0:
            divergent.update(disagree_list)
        elif len(disagree_list) >= minimum and len(agree_list) > 0:
            divergent.update(agree_list)
        else:
            pass

        return divergent

    def get_divergent_nodes(self, histories):
        divergent = set()

        ballot_dict = self.get_ballot_dict(histories)

        for _, state_dict in ballot_dict.items():
            for _, ballot_list in state_dict.items():
                divergent_voting_nodes = self.get_divergent_voting_nodes(ballot_list)
                divergent.update(divergent_voting_nodes)

        return divergent


class NoVotingAuditor(BaseAuditor):
    def _log_name(self):
        return 'faulty-node.no-voting'

    def _log_metric(self, prev_checkpoint, history):
        voted_nodes = set()
        for i in history:
            if i['node'] in voted_nodes or i['node'] == self.consensus.node_name:
                continue

            voted_nodes.add(i['node'])

        no_voting_nodes = list(self.validator_names - voted_nodes)
        [self.consensus.set_faulty_validator(node_name) for node_name in no_voting_nodes]

        self.log.metric(
            checkpoint=prev_checkpoint,
            validators=list(self.validator_names),
            voted_nodes=list(voted_nodes),
            no_voting_nodes=no_voting_nodes,
        )


AUDITORS = (
    DivergentAuditor,
    NoVotingAuditor,
    LivenessAuditor,
)


class FaultyNodeAuditor:
    def __init__(self, blockchain, loop, audit_waiting, audit_time_limit=INFINITE):
        self.blockchain = blockchain
        self.loop = loop
        self.audit_waiting = audit_waiting
        self.audit_time_limit = audit_time_limit

        self.log = logger.get_logger('audit.faulty-node', node=self.blockchain.consensus.node.name)

    def get_coroutines(self):
        auditor_coroutines = list()
        for auditor in AUDITORS:
            auditor_coroutines.append(auditor(self.blockchain, self.loop, self.audit_waiting, self.audit_time_limit).coroutine())

        return auditor_coroutines
