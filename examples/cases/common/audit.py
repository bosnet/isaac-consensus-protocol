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

    async def coroutine(self):
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
            await asyncio.sleep(0.3)

        self.log.debug('started to audit; validators connected')

        while True:
            await asyncio.sleep(0.2)
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
            if now - last_allconfirm_history['received'] < self.auditing_timeout:
                continue

            prev_checkpoint = self.checkpoint
            self.checkpoint = len(self.consensus.voting_histories)

            voted_nodes = set()
            for i in filter(lambda x: x['ballot_id'] == last_allconfirm_history['ballot_id'], histories):
                if i['node'] in voted_nodes or i['node'] == self.consensus.node_name:
                    continue

                voted_nodes.add(i['node'])

            self.log.metric(
                checkpoint=prev_checkpoint,
                validators=list(self.validator_names),
                voted_nodes=list(voted_nodes),
                no_voting_nodes=list(self.validator_names - voted_nodes),
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
