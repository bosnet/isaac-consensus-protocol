# Verifying Quroum Safety of Flower Form

Create a topology case that can actually operate on the network.

## Running

The `run-case.py` will just launch servers, which are instructed by designed yaml file, so to occur consensus, we need to run `run-client.py` to send message to server.

```sh
$ cd ./examples/cases
```

## Quorum Design

* We have 4 quorums shaped like flowers.
* Four nodes are included as validators in all nodes, and the other nodes are attached like petals.
    * Commons: n0 n1 n2 n3
    * q0:
      - validators: n0 n1 n2 n3 n4
    * q1:
      - validators: n0 n1 n2 n3 n5
    * q2:
      - validators: n0 n1 n2 n3 n6
    * q3:
      - validators: n0 n1 n2 n3 n7

## None Faulty Nodes: `flower-form.yml`

```sh
$ python run-case-local-socket.py -log-level error quorum-safety/flower-form/flower-form.yml -log-output-metric /tmp/flower.json
```

### Verifying In Logs

* the important metric messages in all nodes
```sh
$ cat /tmp/flower.json | jq -S --indent 0 -r 'select(.action=="safety_check")' 2> /dev/null
```

> To run this bash script, we need `jq`. To install `jq`, `brew install jq`.

```json
{"action":"safety_check","created":1522136444.0832052,"logger":"consensus.state","result":"success"}
```

Without the faulty node, all nodes were reached the consensus.

## With One Faulty Node: `flower-form-f1.yml`

```sh
$ python run-case-local-socket.py -log-level error quorum-safety/flower-form/flower-form-f1.yml -log-output-metric /tmp/flower-f1.json
```

### Verifying In Logs

* the important metric messages in all nodes
```sh
$ cat /tmp/flower-f1.json | jq -S --indent 0 -r 'select(.action=="safety_check")' 2> /dev/null
```

> To run this bash script, we need `jq`. To install `jq`, `brew install jq`.

```json
{"action":"safety_check","created":1522136431.3979268,"logger":"consensus.state","result":"success"}
```

Even though there is one faulty node, the other nodes have reached the consensus.

## With Two Faulty Nodes: `flower-form-f2.yml`

```sh
$ python run-case-local-socket.py -log-level error quorum-safety/flower-form/flower-form-f2.yml -log-output-metric /tmp/flower-f2.json
```

### Verifying In Logs

* the important metric messages in all nodes
```sh
$ cat /tmp/flower-f2.json | jq -S --indent 0 -r 'select(.action=="safety_check")' 2> /dev/null
```

> To run this bash script, we need `jq`. To install `jq`, `brew install jq`.

```json
{"action":"safety_check","created":1522136431.3979268,"logger":"consensus.state","result":"success"}
```

Even though there is two faulty nodes, the other nodes have reached the consensus.

## With Three Faulty Nodes: `flower-form-f3.yml`

```sh
$ python run-case-local-socket.py -log-level error quorum-safety/flower-form/flower-form-f3-failed.yml -log-output-metric /tmp/flower-f3-failed.json
```

### Verifying In Logs

* the important metric messages in all nodes
```sh
$ cat /tmp/flower-f3-failed.json | jq -S --indent 0 -r 'select(.action=="safety_check")' 2> /dev/null
```

> To run this bash script, we need `jq`. To install `jq`, `brew install jq`.

```json
{"action":"safety_check","created":1522136406.095058,"info":"empty messages","logger":"consensus.state","result":"fail"}
```

When there are three faulty nodes, the other nodes have not reached the consensus.
