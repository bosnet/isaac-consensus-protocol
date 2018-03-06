# Simulation and Testing For Faulty Node: Divergent Voting Nodes

For detailed process of this issues, please check [BOS-172](https://blockchainos.atlassian.net/browse/BOS-172).

## Running

The `run-case.py` will just launch the servers, which are instructed by design yaml file, so to occur the consensus, we need to run `run-client.py` to send message to server.

```
$ cd ./examples/faulty-nodes/divergent-voting
```

The basic usage is,
```
$ python run-case.py -h
usage: run-case.py [-h] [-verbose]
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
$ python run-case.py -log-level info example.yml
```

The 'debug' will produce so massive messages :) To make something happened, run `run-client.py`,

```
$ run-client.py  -p 54320
```

The `54320` is already assigned port by the `example.yml` for the node, 'n1'. In `example.yml`, the faulty nodes are 'n0' and 'n6', which will be faulty node in 100%, `faulties.<node>.n0.case.frequency` is `100`.

## Check Logs

The `run-case.py` will produce this kind of messages as 'metric' log. In `run-case.py`, the `DivergentAuditor()` will be running simultaneously, it checks the `Fba.voting_history = list()` and after the final consensus state, `ALLCONFIRM`, it will filter the `divergent_node` per each node.

```
● 1517463534.81830812 - audit.faulty-node.divergent-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n7",
    "n0",
    "n2",
    "n3"
  ],
  "divergent_voting_nodes": [
    "n0"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n1",
  "created": 1517463534.818308
}
● 1517463534.81902385 - audit.faulty-node.divergent-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n7",
    "n0",
    "n5",
    "n4"
  ],
  "divergent_voting_nodes": [
    "n0"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n6",
  "created": 1517463534.8190238
}
● 1517463534.81953192 - audit.faulty-node.divergent-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n6",
    "n1",
    "n2",
    "n5"
  ],
  "divergent_voting_nodes": [
    "n6"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n7",
  "created": 1517463534.819532
}
● 1517463534.82003880 - audit.faulty-node.divergent-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n1",
    "n7",
    "n0",
    "n3"
  ],
  "divergent_voting_nodes": [
    "n0"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n2",
  "created": 1517463534.8200388
}
● 1517463534.82052612 - audit.faulty-node.divergent-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n1",
    "n0",
    "n2",
    "n5"
  ],
  "divergent_voting_nodes": [
    "n0"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n3",
  "created": 1517463534.8205261
}
● 1517463534.82070994 - audit.faulty-node.divergent-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n6",
    "n1",
    "n5"
  ],
  "divergent_voting_nodes": [],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n4",
  "created": 1517463534.82071
}
● 1517463534.84274697 - audit.faulty-node.divergent-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n6",
    "n7",
    "n4",
    "n3"
  ],
  "divergent_voting_nodes": [
      "n6"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n5",
  "created": 1517463534.842747
}
● 1517463536.81973505 - audit.faulty-node.divergent-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n6",
    "n1",
    "n2",
    "n5",
    "n4",
    "n3"
  ],
  "divergent_voting_nodes": [],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n0",
  "created": 1517463536.819735
}
```
