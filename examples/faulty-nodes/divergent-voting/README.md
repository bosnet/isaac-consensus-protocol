# Simulation and Testing For Faulty Node: Divergent Voting Nodes

For detailed process of this issues, please check [BOS-172](https://blockchainos.atlassian.net/browse/BOS-172).

## Running

The `run.py` will just launch the servers, which are instructed by design yaml file, so to occur the consensus, we need to run `run-client.py` to send message to server.

```
$ cd ./examples/faulty-nodes/divergent-voting
```

The basic usage is,
```
$ python run.py -h
usage: run.py [-h] [-verbose]
              [-log-level {critical,fatal,error,warn,warning,info,debug}]
              [-log-output LOG_OUTPUT] [-log-output-metric LOG_OUTPUT_METRIC]
              [-log-show-line] [-log-no-color]
              design

positional arguments:
  design                network design yaml

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
```

```
$ python run.py -log-level info example.yml
```

The 'debug' will produce so massive messages :) To make something happened, run `run-client.py`,

```
$ run-client.py  -p 54320
```

The `54320` is already assigned port by the `example.yml` for the node, 'n1'. In `example.yml`, the faulty nodes are 'n1' and 'n7', which will be faulty node in 100%, `faulties.<node>.n0.case.frequency.per_consensus` is `100`.

## Check Logs

The `run.py` will produce this kind of messages as 'metric' log. In `run.py`, the `NoVotingAuditor()` will be running simultaneously, it checks the `Blockchain.voting_history = list()` and after the final consensus state, `ALLCONFIRM`, it will filter the `divergent_node` per each node.

```
● 1517292684.32862997 - audit.faulty-node.divergent-voting - METRI - {
  "checkpoint": 0,
  "validators": [
    "n0",
    "n7",
    "n3",
    "n1"
  ],
  "normal_voting_nodes": [],
  "divergent_voting_nodes": [],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n2",
  "created": 1517292684.32863
}
● 1517292684.32913899 - audit.faulty-node.divergent-voting - METRI - {
  "checkpoint": 0,
  "validators": [
    "n0",
    "n2",
    "n5",
    "n1"
  ],
  "normal_voting_nodes": [
    "n5",
    "n1",
    "n2"
  ],
  "divergent_voting_nodes": [
    "n0"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n3",
  "created": 1517292684.329139
}
● 1517292684.32958603 - audit.faulty-node.divergent-voting - METRI - {
  "checkpoint": 0,
  "validators": [
    "n3",
    "n6",
    "n2",
    "n4",
    "n5",
    "n1"
  ],
  "normal_voting_nodes": [
    "n1",
    "n3",
    "n2",
    "n6"
  ],
  "divergent_voting_nodes": [],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n0",
  "created": 1517292684.329586
}
● 1517292684.33796883 - audit.faulty-node.divergent-voting - METRI - {
  "checkpoint": 0,
  "validators": [
    "n6",
    "n2",
    "n5",
    "n1"
  ],
  "normal_voting_nodes": [
    "n5",
    "n1",
    "n2",
    "n6"
  ],
  "divergent_voting_nodes": [],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n7",
  "created": 1517292684.3379688
}
● 1517292686.32920408 - audit.faulty-node.divergent-voting - METRI - {
  "checkpoint": 0,
  "validators": [
    "n0",
    "n7",
    "n3",
    "n2"
  ],
  "normal_voting_nodes": [],
  "divergent_voting_nodes": [],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n1",
  "created": 1517292686.329204
}
● 1517292686.33538413 - audit.faulty-node.divergent-voting - METRI - {
  "checkpoint": 0,
  "validators": [
    "n5",
    "n1",
    "n6"
  ],
  "normal_voting_nodes": [
    "n5",
    "n6"
  ],
  "divergent_voting_nodes": [],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n4",
  "created": 1517292686.3353841
}
● 1517292686.34087205 - audit.faulty-node.divergent-voting - METRI - {
  "checkpoint": 0,
  "validators": [
    "n7",
    "n3",
    "n6",
    "n4"
  ],
  "normal_voting_nodes": [
    "n3",
    "n4",
    "n6"
  ],
  "divergent_voting_nodes": [
    "n7"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n5",
  "created": 1517292686.340872
}
● 1517292686.34133291 - audit.faulty-node.divergent-voting - METRI - {
  "checkpoint": 0,
  "validators": [
    "n0",
    "n7",
    "n4",
    "n5"
  ],
  "normal_voting_nodes": [],
  "divergent_voting_nodes": [],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n6",
  "created": 1517292686.341333
}
```
