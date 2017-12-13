import logging
from state import (
    State,
    NoneState,
    SignState,
    InitState,
    AcceptState,
    AllConfirmState
)
from ballot import Ballot
import threading
import requests

import urllib

log = logging.getLogger(__name__)


class Request(threading.Thread):
    def __init__(self, url, ballot):
        super(Request, self).__init__()
        self.url = url
        self.ballot = ballot

    def run(self):
        try:
            response = requests.post(urllib.parse.urljoin(self.url, '/send_ballot'), params=self.ballot.to_dict())
            if response.status_code == 200:
                log.info('message to %s sent!' % self.url)
        except requests.exceptions.ConnectionError:
            log.info('Connection Refused!')
        return


class Node:
    def __init__(self, node_id, address, threshold, validator_addrs):
        assert type(address) in (list, tuple) and len(address) == 2
        assert type(address[0]) in (str,) and type(address[1]) in (int,)

        self.node_id = node_id
        self.address = address
        self.validator_addrs = validator_addrs
        self.validators = []
        self.threshold = threshold
        self.n_th = len(self.validator_addrs) * self.threshold // 100
        self.validator_ballots = {}
        self.message = ''

        self.state_none = NoneState(self)
        self.state_init = InitState(self)
        self.state_sign = SignState(self)
        self.state_accept = AcceptState(self)
        self.state_all_confirm = AllConfirmState(self)

        self.node_state = self.state_none

    def set_state_init(self):
        self.node_state = self.state_init
        log.debug('node %s state to INIT', self.node_id)

    def set_state_sign(self):
        self.node_state = self.state_sign
        log.debug('node %s state to SIGN', self.node_id)

    def set_state_accept(self):
        self.node_state = self.state_accept
        log.debug('node %s state to ACCEPT', self.node_id)

    def set_state_all_confirm(self):
        self.node_state = self.state_all_confirm
        log.debug('node %s state to ALLCONFIRM', self.node_id)

    def __repr__(self):
        return '<Node: %s(%s)>' % (self.node_id, self.endpoint)

    def __str__(self):
        return '<Node[%s]: %s(%s)>' % (self.node_state.__str__(), self.node_id, self.endpoint)

    @property
    def endpoint(self):
        return 'http://%s:%s' % self.address

    def to_dict(self):
        return dict(
            node_id=self.node_id,
            address=self.address,
            endpoint=self.endpoint,
            validator_addrs=self.validator_addrs,
            threshold=self.threshold,
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
        self.node_state.init_node()
        return

    def receive_from_client(self, message):
        assert isinstance(message, str)
        self.message = message.strip('"\'')
        self.broadcast(self.message)
        return

    def send_to(self, url, ballot):
        log.debug('[%s] send to %s' % (self.node_id, url))
        # t = Request(url, ballot)
        # t.start()
        # t.join()
        try:
            response = requests.post(urllib.parse.urljoin(url, '/send_ballot'), params=ballot.to_dict())
            if response.status_code == 200:
                log.debug('[%s] Sent to %s!' % (self.node_id, url))
        except requests.exceptions.ConnectionError:
            log.debug('[%s] Connection to %s Refused!' % (self.node_id, url))
        return

    def broadcast(self, message):
        log.debug('%s broadcast to everyone' % self.node_id)
        ballot = Ballot(1, self.node_id, message, self.node_state.kind)
        self.receive(ballot)
        for addr in self.validator_addrs:
            url = 'http://%s' % addr
            self.send_to(url, ballot)
        return

    def receive(self, ballot):
        assert isinstance(ballot, Ballot)
        log.debug('[%s] receive ballot from %s ' % (self.node_id, ballot.node_id))
        if self.node_state.kind == ballot.node_state_kind:
            self.node_state.handle_ballot(ballot)
        return

    def store(self, ballot):
        self.validator_ballots[ballot.node_id] = ballot
        return
