import json
import logging
import requests
import urllib

from .ballot import Ballot
from .consensus import BaseConsensus


log = logging.getLogger(__name__)


class Node:
    def __init__(self, node_id, address, threshold, validator_addrs, consensus):
        assert type(address) in (list, tuple) and len(address) == 2
        assert type(address[0]) in (str,) and type(address[1]) in (int,)
        assert isinstance(consensus, BaseConsensus)

        self.node_id = node_id
        self.address = address
        self.validators = dict((key, False) for key in validator_addrs)
        self.threshold = threshold
        self.minimum_number_of_agreement = (1 + len(self.validators)) * self.threshold // 100
        self.validator_ballots = {}
        self.messages = []

        self.consensus = consensus
        self.consensus.set_node(self)
        self.consensus.initialize()

    # def set_state_init(self):
    #     log.info('[%s] state to INIT', self.node_id)
    #     self.node_state = self.state_init

    # def set_state_sign(self):
    #     log.info('[%s] state to SIGN', self.node_id)
    #     self.node_state = self.state_sign

    # def set_state_accept(self):
    #     log.info('[%s] state to ACCEPT', self.node_id)
    #     self.node_state = self.state_accept

    # def set_state_all_confirm(self):
    #     log.info('[%s] state to ALLCONFIRM', self.node_id)
    #     self.node_state = self.state_all_confirm
    #     self.save_message(self.validator_ballots[self.node_id].message)

    def __repr__(self):
        return '<Node: %s(%s)>' % (self.node_id, self.endpoint)

    def __str__(self):
        return '<Node[%s]: %s(%s)>' % (
            self.consensus.node_state.__str__(),
            self.node_id,
            self.endpoint,
        )

    @property
    def endpoint(self):
        return 'http://%s:%s' % tuple(self.address)

    def to_dict(self):
        return dict(
            status=self.consensus.node_state.kind.name,
            node_id=self.node_id,
            threshold=self.threshold,
            address=self.address,
            endpoint=self.endpoint,
            validator_addrs=self.validators,
            messages=self.messages
        )

    def __eq__(self, rhs):
        rhs_endpoint = rhs.endpoint
        lhs_endpoint = self.endpoint

        t_str = '//localhost:'  # target_string
        r_str = '//127.0.0.1:'  # replace_string
        if t_str in rhs_endpoint:
            rhs_endpoint.replace(t_str, r_str)

        if t_str in lhs_endpoint:
            lhs_endpoint.replace(t_str, r_str)
        return lhs_endpoint == rhs_endpoint

    def init_node(self):
        self.consensus.node_state.init_node()
        return

    def receive_message_from_client(self, message):
        assert isinstance(message, str)
        self.broadcast(message.strip('"\''))
        return

    def broadcast(self, message):
        log.debug('[%s] begin broadcast to everyone' % self.node_id)
        ballot = Ballot(1, self.node_id, message, self.consensus.node_state.kind)
        self.send_to(self.endpoint, ballot)
        for addr in self.validators.keys():
            self.send_to(addr, ballot)
        return

    def send_to(self, addr, ballot):
        log.debug('[%s] begin send_to %s' % (self.node_id, addr))
        post_data = json.dumps(ballot.to_dict())
        try:
            response = requests.post(urllib.parse.urljoin(addr, '/send_ballot'), data=post_data)
            if response.status_code == 200:
                log.debug('[%s] sent to %s!' % (self.node_id, addr))
        except requests.exceptions.ConnectionError:
            log.error('[%s] Connection to %s Refused!' % (self.node_id, addr))
        return

    def receive_ballot(self, ballot):
        assert isinstance(ballot, Ballot)
        log.debug('[%s] receive ballot from %s ' % (self.node_id, ballot.node_id))
        if self.consensus.node_state.kind == ballot.node_state_kind:
            self.consensus.node_state.handle_ballot(ballot)
        return

    def store(self, ballot):
        self.validator_ballots[ballot.node_id] = ballot
        return

    def save_message(self, message):
        self.messages.append(message)

    def all_validators_connected(self):
        for _, connected in self.validators.items():
            if connected is False:
                return False
        return True
