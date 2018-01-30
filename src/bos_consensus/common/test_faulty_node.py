from ..network import Endpoint
from .node import node_factory
from .faulty_node import FaultyNodeKind


def test_get_faulty_kind():
    assert FaultyNodeKind.get_faulty_kind('node_unreachable') == FaultyNodeKind.NodeUnreachable
    assert FaultyNodeKind.get_faulty_kind('no_voting') == FaultyNodeKind.NoVoting
    assert FaultyNodeKind.get_faulty_kind('duplicated_message_sent') == FaultyNodeKind.DuplicatedMessageSent
    assert FaultyNodeKind.get_faulty_kind('divergent_voting') == FaultyNodeKind.DivergentVoting
    assert FaultyNodeKind.get_faulty_kind('state_regression') == FaultyNodeKind.StateRegression


def test_instanciation():
    faulty_node = node_factory('n1', Endpoint.from_uri('http://localhost:5001'), 10, 'no_voting')
    assert str(faulty_node) == '<FaultyNode: name=n1 endpoint=http://localhost:5001?name=n1 faulty_kind=FaultyNodeKind.NoVoting faulty_percent=10]>'  # noqa
