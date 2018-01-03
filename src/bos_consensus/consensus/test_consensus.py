from . import get_consensus_module


def test_import_consensus():
    m = get_consensus_module('simple_fba')

    assert m is not None
    assert m.__name__.split('.')[-1] == 'simple_fba'


def test_import_unknown_consensus():
    m = get_consensus_module('i-dont-know')

    assert m is None
