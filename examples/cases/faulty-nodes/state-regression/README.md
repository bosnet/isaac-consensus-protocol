# Creating and Filtering State Regression Ballot

## Faulty Nodes Design

```
nodes:
    ...
    n1:
        port: 54320
        quorum:
            validators:
                - n0
                - n2
...
faulties:
    n1:
        - case:
            kind: state_regression
            frequency: 10  # how often make regressed state within one consensus
            target_nodes:
                - n0
                - n2
```

This design will make `n1` to be the faulty node for `state_regression`. It will make 'state regression' ballot at 10% in one consensus and this ballot will only be sent to `n0` and `n2`.

## Running

```
$ cd ./examples/faulty-nodes
$ python run-case.py -h
usage: run-case.py [-h] [-verbose]
                   [-log-level {critical,fatal,error,warn,warning,info,debug}]
                   [-log-output LOG_OUTPUT]
                   [-log-output-metric LOG_OUTPUT_METRIC] [-log-show-line]
                   [-log-no-color] [-case CASE]
                   design

positional arguments:
  design                design yaml

optional arguments:
  -h, --help            show this help message and exit
  -verbose              verbose log (default: False)
  -log-level {critical,fatal,error,warn,warning,info,debug}
                        set log level (default: debug)
  -log-output LOG_OUTPUT
                        set log output file (default: None)
  -log-output-metric LOG_OUTPUT_METRIC
                        set metric output file (default: None)
  -log-show-line        show seperate lines in log (default: False)
  -log-no-color         disable colorized log message by level (default:
                        False)
  -case CASE            set the case name (default: None)
```

```
$ cd ./examples/faulty-nodes
$ python run-case.py state-regression/example.yml
```

and then, send message to `n1`
```
$ run-client.py -p 54320
```

## Found State Regression Ballots

```
1517392848.00038600 - __main__ - INFO - design loaded:
{'common': {'network': 'default_http',
            'network_module': <module 'bos_consensus.network.default_http' from '/Users/spikeekips/workspace/blockchainos/prototype-fba/src/bosnet-prototype-fba/src/bos_consensus/network/default_http/__init__.py'>,
            'threshold': 60},
 'faulties': {'n1': [BOSDict(kind=<FaultyNodeKind.StateRegression: 5>, frequency=10, target_nodes=['n0', 'n2'])]},
...
1517397563.69022417 - transport.faulty - DEBU - this ballot is under faulty, BOSDict(kind=<FaultyNodeKind.StateRegression: 5>, frequency=10, target_nodes=['n0', 'n2']), but not this time - {'node': 'n1'}
...
1517397644.27706003 - transport.faulty - DEBU - this ballot is under faulty, BOSDict(kind=<FaultyNodeKind.StateRegression: 5>, frequency=100, target_nodes=['n0', 'n2']) - {'node': 'n1'}
1517397644.27696991 - transport.faulty - DEBU - sent intentionally manipulated ballot=<Ballot: ballot_id=c6917f9c067811e8afd68c85903262b4 node_name=n1 state=IsaacState.INIT message=<Message: c6016876067811e8b28a8c85903262b4> result=BallotVotingResult.agree> to=n0 previous_ballot=<Ballot: ballot_id=c6917f9c067811e8afd68c85903262b4 node_name=n1 state=IsaacState.ACCEPT message=<Message: c6016876067811e8b28a8c85903262b4> result=BallotVotingResult.agree> - {'node': 'n1'}
1517392859.07465196 - consensus - DEBU - found state regression ballot=<Ballot: ballot_id=a26418e2066d11e8ab898c85903262b4 node_name=n0 state=IsaacState.INIT message=<Message: a247ce46066d11e89bcc8c85903262b4> result=BallotVotingResult.agree> state=IsaacState.SIGN - {'node': 'n2'}
...
1517392859.08530498 - consensus - DEBU - found state regression ballot=<Ballot: ballot_id=a26418e2066d11e8ab898c85903262b4 node_name=n2 state=IsaacState.INIT message=<Message: a247ce46066d11e89bcc8c85903262b4> result=BallotVotingResult.agree> state=IsaacState.SIGN - {'node': 'n1'}
...
```
