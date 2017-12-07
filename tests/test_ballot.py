from ballot import Ballot

def test_ballot_str():
    assert str(Ballot(1, 'message')) == '[1]: message'