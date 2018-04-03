# ISAAC Consensus Protocol

Validate the consensus model of the FBA


## Notice

**This is not a repository for running a node. This is only a proof of concept for BOSCoin's ISAAC consensus protocol. Feel free to test.**

## Installation

To install and deploy the source, you need to install these packages,

 - python: 3.6 or higher
 - pip

Clone this repository and then run below command.

```sh
$ python setup.py develop
```

## Deployment

```sh
$ run-blockchain.py -h
usage: run-blockchain.py [-h] [-verbose]
                         [-log-level {critical,fatal,error,warn,warning,info,debug}]
                         [-log-output LOG_OUTPUT]
                         [-log-output-metric LOG_OUTPUT_METRIC]
                         [-log-show-line] [-log-no-color]
                         conf

positional arguments:
  conf                  ini config file for server node

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

### Running Node Server

Set the config file.

```sh
$ run-blockchain.py examples/node5001.ini
2017-12-06 15:21:48,459 - __main__ - DEBUG - Node ID: 5001
2017-12-06 15:21:48,459 - __main__ - DEBUG - Node PORT: 5001
2017-12-06 15:21:48,459 - __main__ - DEBUG - Validators: ['localhost:5002', 'localhost:5003']
```

Run the other nodes like this.

```sh
$ run-blockchain.py examples/node5002.ini
$ run-blockchain.py examples/node5003.ini
```

### Running Message Client, `run-client.py`

```sh
$ run-client.py  -h
usage: run-client.py [-h] [-verbose]
                     [-log-level {critical,fatal,error,warn,warning,info,debug}]
                     [-log-output LOG_OUTPUT]
                     [-log-output-metric LOG_OUTPUT_METRIC] [-log-show-line]
                     [-log-no-color] [-m MESSAGE] [-i IP] [-p PORT]

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
  -m MESSAGE, --message MESSAGE
                        Messages you want to send to the server (default:
                        Quaerat)
  -i IP, --ip IP        Server IP you want to send the message to (default:
                        localhost)
  -p PORT, --port PORT  Server port you want to send the message to (default:
                        5001)
```

After checking node state in cmd line, then run client like this.
Send one message to `5001`

```sh
$ run-client.py --ip "localhost" --port 5001 --message "message"
```

Send five messages at a time every 4 seconds to `5001`

```sh
$ for i in $(seq 5)
do
    run-client.py \
        --ip localhost \
        --port 5001 \
        --message "message-$i"
        sleep 4
done
```

Send five messages at a time every 4 seconds to `5001` and `5002`,

```sh
$ for port in 5001 5002
do
    for i in $(seq 5)
    do
        run-client.py \
            --ip localhost \
            --port $port \
            --message "message-$i"
            sleep 4
    done
done
```

Send five messages at a time every 4 seconds to `5000`-`5003` randomly three times

```sh
$ for _ in $(seq 3)
do
    p=$(expr $RANDOM % 4)
    for i in $(seq 5)
    do
        run-client.py \
            --ip localhost \
            --port "500$p" \
            --message "message-$i"
            sleep 4
    done
done
```

## Test

```sh
$ pytest
$ flake8
```

## Examples

See the [examples](./examples/).


## `send-message.py`

> Before running this script, please run `python setup.py develop`.

```sh
$ send-message.py -h
usage: send-message.py [-h] [-verbose]
                       [-log-level {critical,fatal,error,warn,warning,info,debug}]
                       [-log-output LOG_OUTPUT]
                       [-log-output-metric LOG_OUTPUT_METRIC] [-log-show-line]
                       [-log-no-color]
                       endpoints [endpoints ...] [message]

positional arguments:
  endpoints             endpoints and it's number of messages, you want to
                        send; ex) http://localhost:80?m=5
                        http://localhost:80?m=10
  message               Messages you want to send to the server (default:
                        None)

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

This script will try to send messages to multiple nodes simultaneously.

```sh
$ send-message.py http://localhost:54320
```

This will send one random message to <http://localhost:54320>.


```sh
$ send-message.py http://localhost:54320 http://localhost:54321
```

This will send one random message to <http://localhost:54320> and <http://localhost:54321> at the same time.

You can set the number of messages for one node like this,

```sh
$ send-message.py http://localhost:54320?m=9 http://localhost:54321?m=10
```

This will send 9 random messages to <http://localhost:54320> and 10 random messages to <http://localhost:54321>.

## `metric-analyzer.py`

This simple script will try to analyze the metric messages from node. Mainly this will handle below issues,

* node activity
* fault tolerance for nodes
* safety between quorum(2 nodes)
* ~~liveness between quorum(2 nodes)~~

The definition of these terms will be found in stellar documentation page or SCP paper, or even in confluence page of BlockchainOS. The interesting thing is that to check the health of quorum, this script will create superset in all the validators and compose the quorum with each 2 nodes.

### Usage

Before running this script, please 'metric' messages from running nodes and make something happened.

For instance, metric logs should be genertated in `/tmp/metric.json`.

```
$ run-blockchain.py examples/node5001.ini -log-output-metric /tmp/metric.json
$ run-blockchain.py examples/node5002.ini -log-output-metric /tmp/metric.json
$ run-blockchain.py examples/node5003.ini -log-output-metric /tmp/metric.json
$ run-blockchain.py examples/node5004.ini -log-output-metric /tmp/metric.json
```

Then send messages to nodes.

```
$ for port in 5001 5002 5003 5004
do
    for i in $(seq 5)
    do
        python scripts/run-client.py \
            --ip localhost \
            --port $port \
            --message "message-$i"
            sleep 2
    done
done
```

```sh
$ metric-analyzer.py -h
usage: metric-analyzer.py [-h] [-verbose]
                          [-log-level {critical,fatal,error,warn,warning,info,debug}]
                          [-log-output LOG_OUTPUT]
                          [-log-output-metric LOG_OUTPUT_METRIC]
                          [-log-show-line] [-log-no-color] [-type TYPE]
                          [-nodes NODES] [-node NODE]
                          [metric]

positional arguments:
  metric                metric file (default: None)

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
  -type TYPE        set the analyzer type to be shown
                        (dict_keys(['history', 'safety', 'fault-tolerance']))
                        (default: None)
  -nodes NODES          set the nodes to be shown (default: None)
```

If you have the `/tmp/metric.json`,

```sh
$ metric-analyzer.py /tmp/metric.json
```

You can filter multiple types you want,

```sh
$ metric-analyzer.py -type safety,fault-tolerance -nodes 5001 /tmp/metric.json
```
This will show result only for safety and fault tolerance of `5001`.
