from ballot import Ballot

def test_ballot_str():
    assert str(Ballot(1, 1, 'message')) == '1:1[None]: message'