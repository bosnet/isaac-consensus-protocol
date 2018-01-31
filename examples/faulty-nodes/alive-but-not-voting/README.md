# Simulation and Testing For Faulty Node: Alive, But Not Voting Nodes

For detailed process of this issues, please check [BOS-164](https://blockchainos.atlassian.net/browse/BOS-164).

## Running

The `run.py` will just launch the servers, which are instructed by design yaml file, so to occur the consensus, we need to run `run-client.py` to send message to server.

```
$ cd ./examples/faulty-nodes/alive-but-not-voting
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

The `54320` is already assigned port by the `example.yml` for the node, 'n1'. In `example.yml`, the faulty nodes are 'n0' and 'n7', which will be faulty node in 100%, `faulties.<node>.n0.case.frequency.per_consensus` is `100`.

## Check Logs

The `run.py` will produce this kind of messages as 'metric' log. In `run.py`, the `NoVotingAuditor()` will be running simultaneously, it checks the `Blockchain.voting_history = list()` and after the final consensus state, `ALLCONFIRM`, it will filter the `no_voting_nodes` per each node.

```
● 1517182997.42433095 - audit.faulty-node.no-voting - METRI - {
  "checkpoint": 0,
  "validators": [ "n7", "n1", "n0", "n3" ],
  "voted_nodes": [ "n3", "n1" ],
  "no_voting_nodes": [ "n0", "n7" ],
  "logger": "audit.faulty-node.no-voting",
  "node": "n2",
  "created": 1517182997.424331
}
● 1517182997.42496991 - audit.faulty-node.no-voting - METRI - {
  "checkpoint": 0,
  "validators": [ "n1", "n0", "n5", "n2" ],
  "voted_nodes": [ "n2", "n5", "n1" ],
  "no_voting_nodes": [ "n0" ],
  "logger": "audit.faulty-node.no-voting",
  "node": "n3",
  "created": 1517182997.42497
}
● 1517182999.42926097 - audit.faulty-node.no-voting - METRI - {
  "checkpoint": 0,
  "validators": [ "n7", "n0", "n3", "n2" ],
  "voted_nodes": [ "n2", "n3", "n1", "n4" ],
  "no_voting_nodes": [ "n0", "n7" ],
  "logger": "audit.faulty-node.no-voting",
  "node": "n1",
  "created": 1517182999.429261
}
● 1517182999.43352795 - audit.faulty-node.no-voting - METRI - {
  "checkpoint": 0,
  "validators": [ "n4", "n7", "n5", "n0" ],
  "voted_nodes": [ "n5", "n4" ],
  "no_voting_nodes": [ "n0", "n7" ],
  "logger": "audit.faulty-node.no-voting",
  "node": "n6",
  "created": 1517182999.433528
}
● 1517182999.43415499 - audit.faulty-node.no-voting - METRI - {
  "checkpoint": 0,
  "validators": [ "n5", "n6", "n1" ],
  "voted_nodes": [ "n5", "n6" ],
  "no_voting_nodes": [ "n1" ],
  "logger": "audit.faulty-node.no-voting",
  "node": "n4",
  "created": 1517182999.434155
}
● 1517182999.43429399 - audit.faulty-node.no-voting - METRI - {
  "checkpoint": 0,
  "validators": [ "n4", "n7", "n6", "n3" ],
  "voted_nodes": [ "n6", "n3", "n4" ],
  "no_voting_nodes": [ "n7" ],
  "logger": "audit.faulty-node.no-voting",
  "node": "n5",
  "created": 1517182999.434294
}
```
