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

The `54320` is already assigned port by the `example.yml` for the node, 'n1'. In `example.yml`, the faulty nodes are 'n0' and 'n6', which will be faulty node in 100%, `faulties.<node>.n0.case.frequency` is `100`.

## Check Logs

The `run.py` will produce this kind of messages as 'metric' log. In `run.py`, the `DivergentAuditor()` will be running simultaneously, it checks the `Blockchain.voting_history = list()` and after the final consensus state, `ALLCONFIRM`, it will filter the `divergent_node` per each node.

```
● 1517380220.95049810 - audit.faulty-node.divergent-voting - METRI - {
  "checkpoint": 0,
  "validators": [
    "n0",
    "n3",
    "n7",
    "n1"
  ],
  "divergent_voting_nodes": [
    "n0"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n2",
  "created": 1517380220.950498
}
● 1517380220.95111489 - audit.faulty-node.divergent-voting - METRI - {
  "checkpoint": 0,
  "validators": [
    "n0",
    "n3",
    "n7",
    "n2"
  ],
  "divergent_voting_nodes": [
    "n0"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n1",
  "created": 1517380220.951115
}
● 1517380220.95158100 - audit.faulty-node.divergent-voting - METRI - {
  "checkpoint": 0,
  "validators": [
    "n0",
    "n1",
    "n5",
    "n2"
  ],
  "divergent_voting_nodes": [
    "n0"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n3",
  "created": 1517380220.951581
}
● 1517380220.95203400 - audit.faulty-node.divergent-voting - METRI - {
  "checkpoint": 0,
  "validators": [
    "n6",
    "n3",
    "n4",
    "n1",
    "n5",
    "n2"
  ],
  "divergent_voting_nodes": [],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n0",
  "created": 1517380220.952034
}
● 1517380220.95539498 - audit.faulty-node.divergent-voting - METRI - {
  "checkpoint": 0,
  "validators": [
    "n6",
    "n3",
    "n4",
    "n7"
  ],
  "divergent_voting_nodes": [
    "n6"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n5",
  "created": 1517380220.955395
}
● 1517380220.95597792 - audit.faulty-node.divergent-voting - METRI - {
  "checkpoint": 0,
  "validators": [
    "n0",
    "n4",
    "n7",
    "n5"
  ],
  "divergent_voting_nodes": [
    "n0"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n6",
  "created": 1517380220.955978
}
● 1517380220.95650196 - audit.faulty-node.divergent-voting - METRI - {
  "checkpoint": 0,
  "validators": [
    "n6",
    "n1",
    "n5",
    "n2"
  ],
  "divergent_voting_nodes": [
    "n6"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n7",
  "created": 1517380220.956502
}
● 1517380222.95162392 - audit.faulty-node.divergent-voting - METRI - {
  "checkpoint": 0,
  "validators": [
    "n1",
    "n5",
    "n6"
  ],
  "divergent_voting_nodes": [],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n4",
  "created": 1517380222.951624
}
```
