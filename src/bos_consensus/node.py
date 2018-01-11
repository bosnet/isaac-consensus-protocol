import logging

from .ballot import Ballot
from .consensus import BaseConsensus
from .network import BaseTransport


log = logging.getLogger(__name__)


class Node:
    node_id = None
    transport = None

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

    def __repr__(self):
        return '<Node: %s(%s)>' % (self.node_id, self.endpoint)

    def __str__(self):
        return '<Node[%s]: %s(%s)>' % (
            self.consensus.node_state.__str__(),
            self.node_id,
            self.endpoint,
        )

    def set_transport(self, transport):
        assert isinstance(transport, BaseTransport)

        self.transport = transport

        return

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

    def clear_validator_ballots(self):
        self.validator_ballots.clear()

    def receive_message_from_client(self, message):
        assert isinstance(message, str)
        self.broadcast(message.strip('"\''))
        return

    def broadcast(self, message):
        log.debug('[%s] begin broadcast to everyone' % self.node_id)
        ballot = Ballot(1, self.node_id, message, self.consensus.node_state.kind)
        self.transport.send(self.endpoint, ballot.to_dict())
        for addr in self.validators.keys():
            self.transport.send(addr, ballot.to_dict())

        return

    def receive_ballot(self, ballot):
        assert isinstance(ballot, Ballot)
        log.debug('[%s] receive ballot from %s ' % (self.node_id, ballot.node_id))
        self.consensus.node_state.handle_ballot(ballot)

    def store(self, ballot):
        # [TODO] when receive different message?
        if self.consensus.node_state.kind <= ballot.node_state_kind:
            self.validator_ballots[ballot.node_id] = ballot
        return

    def save_message(self, message):
        self.messages.append(message)

    def all_validators_connected(self):
        for _, connected in self.validators.items():
            if not connected:
                return False

        return True
