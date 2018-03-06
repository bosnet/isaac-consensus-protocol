import asyncio

from bos_consensus.util import (
    datetime_to_timestamp,
    logger,
    utcnow,
)


class NoVotingAuditor:
    checkpoint = None
    loop = None
    auditing_timeout = None

    def __init__(self, blockchain, loop, auditing_timeout):
        super(NoVotingAuditor, self).__init__()

        self.consensus = blockchain.consensus
        self.loop = loop
        self.checkpoint = 0
        self.auditing_timeout = auditing_timeout

        self.log = logger.get_logger('audit.faulty-node.no-voting', node=self.consensus.node.name)

        self.validator_names = set(map(lambda x: x.name, self.consensus.validator_candidates))

    def _wait_for_connecting_validators(self):
        if not self.consensus.all_validators_connected():
            return False

        return True

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
            await asyncio.sleep(0.3)

        self.log.debug('started to audit; validators connected')

        while True:
            await asyncio.sleep(0.2)
            histories = self.consensus.voting_histories[self.checkpoint:]

            if len(histories) < 1:
                continue

            last_voting_idx = self.get_last_voting_idx(histories)
            if last_voting_idx is None:
                continue

            last_voting_history = histories[last_voting_idx]
            now = datetime_to_timestamp(utcnow())
            if now - last_voting_history['received'] < self.auditing_timeout:
                continue

            prev_checkpoint = self.checkpoint
            self.checkpoint = len(self.consensus.voting_histories)

            voted_nodes = set()
            for i in filter(lambda x: x['ballot_id'] == last_voting_history['ballot_id'], histories):
                if i['node'] in voted_nodes or i['node'] == self.consensus.node_name:
                    continue

                voted_nodes.add(i['node'])

            no_voting_nodes = list(self.validator_names - voted_nodes)
            [self.consensus.set_faulty_validator(node_name) for node_name in no_voting_nodes]

            if not self.consensus.is_guarantee_liveness():
                self.log.metric(
                    liveness='Failed',
                    minimum=self.consensus.minimum,
                    validators=list(self.consensus.validator_connected),
                    faulties=self.consensus.validator_faulty,
                )

            self.log.metric(
                checkpoint=prev_checkpoint,
                validators=list(self.validator_names),
                voted_nodes=list(voted_nodes),
                no_voting_nodes=no_voting_nodes,
            )

        return


AUDITORS = (
    NoVotingAuditor,
)


class FaultyNodeAuditor:
    def __init__(self, blockchain, loop, auditing_timeout):
        self.blockchain = blockchain
        self.loop = loop
        self.auditing_timeout = auditing_timeout

        self.log = logger.get_logger('audit.faulty-node', node=self.blockchain.consensus.node.name)

    async def start(self):
        for auditor in AUDITORS:
            await auditor(self.blockchain, self.loop, self.auditing_timeout).coroutine()
        return
