# Simulation and Testing For Faulty Node: Divergent Voting Nodes

For detailed process of this issues, please check [BOS-172](https://blockchainos.atlassian.net/browse/BOS-172).

## Running by Http Protocol

The `run-case.py` will just launch the servers, which are instructed by design yaml file, so to occur the consensus, we need to run `run-client.py` to send message to server.

```
$ cd ./examples/cases
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
$ python run-case.py -log-level info faulty-nodes/divergent-voting/example.yml
```

The 'debug' will produce so massive messages :) To make something happened, run `run-client.py`,

```
$ run-client.py  -p 54320
```

The `54320` is already assigned port by the `example.yml` for the node, 'n1'. In `example.yml`, the faulty nodes are 'n0' and 'n6', which will be faulty node in 100%, `faulties.<node>.n0.case.frequency` is `100`.

## Check Logs

The `run-case.py` will produce this kind of messages as 'metric' log. In `run-case.py`, the `DivergentAuditor()` will be running simultaneously, it checks the `Fba.voting_history = list()` and after the final consensus state, `ALLCONFIRM`, it will filter the `divergent_node` per each node.

```
● 1520317475.90061212 - audit.faulty-node.divergent-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n2",
    "n5",
    "n4",
    "n1",
    "n3",
    "n6"
  ],
  "divergent_voting_nodes": [],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n0",
  "created": 1520317475.900612
}
● 1520317475.90118909 - audit.faulty-node.no-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n2",
    "n5",
    "n4",
    "n1",
    "n3",
    "n6"
  ],
  "voted_nodes": [
    "n1",
    "n3",
    "n2",
    "n6"
  ],
  "no_voting_nodes": [
    "n5",
    "n4"
  ],
  "logger": "audit.faulty-node.no-voting",
  "node": "n0",
  "created": 1520317475.901189
}
● 1520317475.90167093 - audit.faulty-node.divergent-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n3",
    "n0",
    "n2",
    "n7"
  ],
  "divergent_voting_nodes": [
    "n0"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n1",
  "created": 1520317475.901671
}
● 1520317475.90206599 - audit.faulty-node.no-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n3",
    "n0",
    "n2",
    "n7"
  ],
  "voted_nodes": [
    "n2",
    "n4",
    "n3",
    "n7",
    "n0"
  ],
  "no_voting_nodes": [],
  "logger": "audit.faulty-node.no-voting",
  "node": "n1",
  "created": 1520317475.902066
}
● 1520317475.90251017 - audit.faulty-node.divergent-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n1",
    "n3",
    "n0",
    "n7"
  ],
  "divergent_voting_nodes": [
    "n0"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n2",
  "created": 1520317475.9025102
}
● 1520317475.90291786 - audit.faulty-node.no-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n1",
    "n3",
    "n0",
    "n7"
  ],
  "voted_nodes": [
    "n1",
    "n3",
    "n0",
    "n7"
  ],
  "no_voting_nodes": [],
  "logger": "audit.faulty-node.no-voting",
  "node": "n2",
  "created": 1520317475.9029179
}
● 1520317475.90329003 - audit.faulty-node.divergent-voting - METR - {
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
  "created": 1520317475.90329
}
● 1520317475.90358710 - audit.faulty-node.no-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n1",
    "n0",
    "n2",
    "n5"
  ],
  "voted_nodes": [
    "n1",
    "n0",
    "n2",
    "n5"
  ],
  "no_voting_nodes": [],
  "logger": "audit.faulty-node.no-voting",
  "node": "n3",
  "created": 1520317475.903587
}
● 1520317475.90390611 - audit.faulty-node.divergent-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n1",
    "n5",
    "n6"
  ],
  "divergent_voting_nodes": [],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n4",
  "created": 1520317475.903906
}
● 1520317475.90418315 - audit.faulty-node.no-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n1",
    "n5",
    "n6"
  ],
  "voted_nodes": [
    "n6",
    "n0",
    "n5"
  ],
  "no_voting_nodes": [
    "n1"
  ],
  "logger": "audit.faulty-node.no-voting",
  "node": "n4",
  "created": 1520317475.9041831
}
● 1520317475.90452409 - audit.faulty-node.divergent-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n7",
    "n6",
    "n3",
    "n4"
  ],
  "divergent_voting_nodes": [
    "n6"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n5",
  "created": 1520317475.904524
}
● 1520317475.90481091 - audit.faulty-node.no-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n7",
    "n6",
    "n3",
    "n4"
  ],
  "voted_nodes": [
    "n4",
    "n3",
    "n7",
    "n6",
    "n0"
  ],
  "no_voting_nodes": [],
  "logger": "audit.faulty-node.no-voting",
  "node": "n5",
  "created": 1520317475.904811
}
● 1520317475.90513992 - audit.faulty-node.divergent-voting - METR - {
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
  "created": 1520317475.90514
}
● 1520317475.90541911 - audit.faulty-node.no-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n7",
    "n0",
    "n5",
    "n4"
  ],
  "voted_nodes": [
    "n4",
    "n0",
    "n5",
    "n7"
  ],
  "no_voting_nodes": [],
  "logger": "audit.faulty-node.no-voting",
  "node": "n6",
  "created": 1520317475.905419
}
● 1520317475.90574217 - audit.faulty-node.divergent-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n1",
    "n2",
    "n5",
    "n6"
  ],
  "divergent_voting_nodes": [
    "n6"
  ],
  "logger": "audit.faulty-node.divergent-voting",
  "node": "n7",
  "created": 1520317475.9057422
}
● 1520317475.90605116 - audit.faulty-node.no-voting - METR - {
  "checkpoint": 0,
  "validators": [
    "n1",
    "n2",
    "n5",
    "n6"
  ],
  "voted_nodes": [
    "n1",
    "n2",
    "n5",
    "n6"
  ],
  "no_voting_nodes": [],
  "logger": "audit.faulty-node.no-voting",
  "node": "n7",
  "created": 1520317475.9060512
}
```

## Running by Local Socket

The `run-case-local-socket.py` will launch the servers, which are instructed by design json or yaml file. Then send a message to the server to confirm that an consensus has been reached.

```
$ cd ./examples/cases
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
$ python run-case-local-socket.py -log-level info faulty-nodes/divergent-voting/example.yml
```

In `example.yml`, the faulty nodes are 'n0' and 'n6', which will be faulty node in 100%, `faulties.<node>.n0.case.frequency` is `100`.
