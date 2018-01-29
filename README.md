# FBA Prototype Of BOSNet

Validate the consensus model of the FBA

## Installation

To install and deploy the source, you need to install these packages,

 - python: 3.5 or higher
 - pip

```
$ pip install virtualenv
$ virtualenv bosnet-prototype-fba
$ cd bosnet-prototype-fba
$ source bin/activate
$ mkdir src/
$ cd src
$ git clone git@github.com:owlchain/bosnet-prototype-fba.git
$ cd bosnet-prototype-fba
```

```
$ python setup.py develop
```

## Deployment

```
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
```
$ run-blockchain.py examples/node5001.ini
2017-12-06 15:21:48,459 - __main__ - DEBUG - Node ID: 5001
2017-12-06 15:21:48,459 - __main__ - DEBUG - Node PORT: 5001
2017-12-06 15:21:48,459 - __main__ - DEBUG - Validators: ['localhost:5002', 'localhost:5003']
```

Run the other nodes like this.
```
$ python run-blockchain.py examples/node5002.ini
$ python run-blockchain.py examples/node5003.ini
```

### Running Message Client, `run-client.py`

```
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
```
$ python scripts/run-client.py --ip "localhost" --port 5001 --message "message"
```

Send five messages at a time every 4 seconds to `5001`
```
for i in $(seq 5)
do
    python scripts/run-client.py \
        --ip localhost \
        --port 5001 \
        --message "message-$i"
        sleep 4
done
```

Send five messages at a time every 4 seconds to `5001` and` 5002`,
```
for port in 5001 5002
do
    for i in $(seq 5)
    do
        python scripts/run-client.py \
            --ip localhost \
            --port $port \
            --message "message-$i"
            sleep 4
    done
done
```

Send five messages at a time every 4 seconds to `5000-5003` randomly three times
```
for _ in $(seq 3)
do
    p=$(expr $RANDOM % 4)
    for i in $(seq 5)
    do
        python scripts/run-client.py \
            --ip localhost \
            --port "500$p" \
            --message "message-$i"
            sleep 4
    done
done
```

## Test

```
$ cd bosnet-prototype-fba
$ pytest
```

## Examples

See the [examples](./examples/).
