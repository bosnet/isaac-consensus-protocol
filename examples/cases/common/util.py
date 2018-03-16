import json
import pprint  # noqa
import sys  # noqa
import threading
import yaml

from bos_consensus.blockchain import Blockchain
from .divergent_voting import DivergentVotingConsensus
from bos_consensus.common.faulty_node import FaultyNodeKind
from bos_consensus.common import node_factory
from bos_consensus.network import Endpoint, get_network_module, BaseServer
from bos_consensus.util import (
    convert_dict_to_namedtuple,
    convert_json_config,
    convert_namedtuple_to_dict,
    get_free_port,
    get_local_ipaddress,
)

from .no_voting import NoVotingMiddleware
from .node_unreachable import (
    NodeUnreachableTransport,
)
from .state_regression import StateRegressionTransport


NETWORK_MODULE = get_network_module('default_http')


def load_design(filename):
    design = None

    with open(filename) as f:
        if filename.split('.')[-1] == 'yml':
            design = convert_dict_to_namedtuple(yaml.load(f.read()))
        elif filename.split('.')[-1] == 'json':
            temp_design = convert_json_config(json.load(f))
            design = convert_dict_to_namedtuple(temp_design)
        else:
            print('# error: \"file `%s` is not valid file. yml or json type is needed\"' % filename)
            sys.exit(1)

    defined_ports = list()
    for name, config in design.nodes._asdict().items():
        port = getattr(config, 'port', None)
        if port is None:
            continue

        defined_ports.append(port)

    faulty_nodes = dict()
    nodes = dict()
    for name, config in design.nodes._asdict().items():
        port = getattr(config, 'port', None)
        if port is None:
            port = get_free_port(defined_ports)

        endpoint = Endpoint(NETWORK_MODULE.SCHEME, get_local_ipaddress(), port, name=name)
        node = node_factory(name, endpoint, 0)

        if hasattr(config.quorum, 'threshold'):
            threshold = config.quorum.threshold
        else:
            threshold = design.common.threshold

        nodes[name] = dict(node=node, quorum=dict(validators=list(), threshold=threshold))

        faulties = list()
        faulty = getattr(getattr(design, 'faulties', None), name, None)
        if faulty is not None:
            for case in faulty:
                kind = FaultyNodeKind.get_from_name(case.case.kind)
                if kind in (FaultyNodeKind.Unknown,):
                    continue

                dict_case = convert_namedtuple_to_dict(case.case)
                dict_case['kind'] = kind
                faulties.append(dict_case)

        if len(faulties) > 0:
            faulty_nodes[name] = faulties

    for name, config in design.nodes._asdict().items():
        for node_name in config.quorum.validators:
            nodes[name]['quorum']['validators'].append(nodes[node_name]['node'])

    design_dict = convert_namedtuple_to_dict(design)

    if 'audit_waiting' not in design_dict['common']:
        design_dict['common']['audit_waiting'] = 1
    if 'audit_time_limit' not in design_dict['common']:
        design_dict['common']['audit_time_limit'] = 2
    design_dict['common']['network_module'] = NETWORK_MODULE
    design_dict['nodes'] = list(nodes.values())
    design_dict['nodes_by_name'] = nodes
    design_dict['faulties'] = faulty_nodes

    return convert_dict_to_namedtuple(design_dict)


class NodeRunner(threading.Thread):
    def __init__(self, blockchain):
        super(NodeRunner, self).__init__()

        self.blockchain = blockchain

    def run(self):
        BaseServer(self.blockchain).start()

        return


class FaultyBlockchain(Blockchain):
    faulties = None
    no_voting_ballot_ids = None  # store the ballot to be skipped

    def __init__(self, faulties, consensus, transport=None):
        self.set_logging('blockchain', node=consensus.node.name)

        found_node_unreachable_faulty = None
        found_state_regression_faulty = None
        found_divergent_voting_faulty = None

        for faulty in faulties:
            if faulty.kind in (FaultyNodeKind.NodeUnreachable,):
                found_node_unreachable_faulty = faulty
                continue

            if faulty.kind in (FaultyNodeKind.StateRegression,):
                found_state_regression_faulty = faulty
                continue

            if faulty.kind in (FaultyNodeKind.DivergentVoting,):
                found_divergent_voting_faulty = faulty
                continue

        if found_node_unreachable_faulty is not None:
            self.log.debug('found node_unreachable faulty case: %s', found_node_unreachable_faulty)
            transport = NodeUnreachableTransport(
                found_node_unreachable_faulty,
                bind=(
                    consensus.node.endpoint.host,
                    consensus.node.endpoint.port,
                ),
            )

        if found_state_regression_faulty is not None:
            self.log.debug('found state_regression faulty case: %s', found_state_regression_faulty)
            transport = StateRegressionTransport(
                found_state_regression_faulty,
                bind=(
                    consensus.node.endpoint.host,
                    consensus.node.endpoint.port,
                ),
            )

        if found_divergent_voting_faulty is not None:
            self.log.debug('found divergent_voting faulty case: %s', found_divergent_voting_faulty)
            divergent_voting_consensus = DivergentVotingConsensus(
                found_divergent_voting_faulty.frequency,
                consensus.node,
                consensus.threshold,
                consensus.validator_candidates,
            )
            divergent_voting_consensus.validator_connected = consensus.validator_connected
            consensus = divergent_voting_consensus

        super(FaultyBlockchain, self).__init__(consensus, transport)

        if found_node_unreachable_faulty:
            self.log.debug('found node_unreachable faulty, so the transport will be replaced by `NodeUnreachableTransport`')  # noqa

        assert type(faulties) in (list, tuple)

        self.no_voting_ballot_ids = list()

        self._load_faulties(faulties)

    def _load_faulties(self, faulties):
        self.log.debug('found %d faulties', len(faulties))
        for faulty in faulties:
            if faulty.kind in (FaultyNodeKind.Unknown,):
                continue

            self.log.debug('trying to load faulty, %s', faulty)
            func = getattr(self, '_handle_%s' % FaultyNodeKind.get_name(faulty.kind), None)
            if func is None:
                continue

            func(faulty)

        return

    def _handle_no_voting(self, faulty):
        middleware_class = type(
            'NoVotingMiddleware-faulty-frequency-%s' % faulty.frequency.per_consensus,
            (NoVotingMiddleware,),
            dict(faulty_frequency=faulty.frequency.per_consensus),
        )
        self.log.debug('load faulty middleware, %s for %s', middleware_class, faulty)
        self.middlewares.insert(0, middleware_class)

        return
