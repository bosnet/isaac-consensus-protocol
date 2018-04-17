# Verifying Quorum Safety of Flower Form

Create a topology case that can actually operate on the network.

## Running

The `run-case.py` will just launch the servers that are constructed by the yaml formatted design file. To verify a message through consensus, we need to run `run-client-new.py` to send message to server.


Substitute the `<DESIGN_FILE>.yml` to run a specific case for flower-form
```sh
$ cd ../../cases
$ python run-case.py -log-level error -log-output-metric /tmp/flower.json quorum-safety/flower-form/<DESIGN_FILE>.yml
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

## No Faulty Nodes: `flower-form.yml`

Substitute the `<DESIGN_FILE>.yml` to `flower-form.yml` in the above example

### Verifying In Logs

* filter important metric messages in all nodes
```sh
$ cat /tmp/flower.json | jq -S --indent 0 -r 'select(.action=="safety_check")' 2> /dev/null
```

> To run this bash script, we need `jq`. To install `jq`, `brew install jq`.

```json
{"action":"safety_check","created":1522136444.0832052,"logger":"consensus.state","result":"success"}
```

Since there are no faulty nodes, all nodes reached consensus.

## With One Faulty Node: `flower-form-f1.yml`

Substitute the `<DESIGN_FILE>.yml` to `flower-form-f1.yml` in the above example

### Verifying In Logs

* filter important metric messages in all nodes
```sh
$ cat /tmp/flower-f1.json | jq -S --indent 0 -r 'select(.action=="safety_check")' 2> /dev/null
```

> To run this bash script, we need `jq`. To install `jq`, `brew install jq`.

```json
{"action":"safety_check","created":1522136431.3979268,"logger":"consensus.state","result":"success"}
```

Even though there is one faulty node, all nodes have reached consensus.

## With Two Faulty Nodes: `flower-form-f2.yml`

Substitute the `<DESIGN_FILE>.yml` to `flower-form-f2.yml` in the above example


### Verifying In Logs

* filter important metric messages in all nodes
```sh
$ cat /tmp/flower-f2.json | jq -S --indent 0 -r 'select(.action=="safety_check")' 2> /dev/null
```

> To run this bash script, we need `jq`. To install `jq`, `brew install jq`.

```json
{"action":"safety_check","created":1522136431.3979268,"logger":"consensus.state","result":"success"}
```

Even though there are two faulty nodes, all nodes have reached consensus.

## With Three Faulty Nodes: `flower-form-f3.yml`

Substitute the `<DESIGN_FILE>.yml` to `flower-form-f3.yml` in the above example

### Verifying In Logs

* filter important metric messages in all nodes
```sh
$ cat /tmp/flower-f3-failed.json | jq -S --indent 0 -r 'select(.action=="safety_check")' 2> /dev/null
```

> To run this bash script, we need `jq`. To install `jq`, `brew install jq`.

```json
{"action":"safety_check","created":1522136406.095058,"info":"empty messages","logger":"consensus.state","result":"fail"}
```

When there are three faulty nodes, the network failed to reach consensus.
