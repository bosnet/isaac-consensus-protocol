from . import get_network_module


def test_import_network():
    m = get_network_module('default_http')

    assert m is not None
    assert m.__name__.split('.')[-1] == 'default_http'


def test_import_unknown_network():
    m = get_network_module('i-dont-know')

    assert m is None
