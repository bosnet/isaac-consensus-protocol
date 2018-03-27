# Performance Test

This module is an experimental module to see how the performance of consensus varies according to various cases.
The results obtained from the experiment are as follows.
1. Find the optimized slot size according to node size.
1. The scalability of how consensus performance degrades with increasing number of nodes.
1. In the same environment, it is to check the performance difference of various consensus algorithms (which are not yet implemented).

>Related issue, please check [BOS-232](https://blockchainos.atlassian.net/browse/BOS-232).

## Running

```sh
$ python examples/experiment/run-consensus-performance.py -log-level error -log-output-metric /tmp/m.json -n 5 -t 100 -b 10 -s 10 -cp isaac
```

> Before running this command, make sure you have run `python setup.py develop`.

## Options
```
usage: run-consensus-performance.py [-h] [-verbose]
                                    [-log-level {critical,fatal,error,warn,warning,info,debug}]
                                    [-log-output LOG_OUTPUT]
                                    [-log-output-metric LOG_OUTPUT_METRIC]
                                    [-log-show-line] [-log-no-color]
                                    [-n NODES] [-t THRESHOLD] [-b BALLOTS]
                                    [-s SENDING] [-cp CONSENSUS_PROTOCOL]

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
  -n NODES, --nodes NODES
                        Number of nodes (default: 5)
  -t THRESHOLD, --threshold THRESHOLD
                        Threshold of all nodes (default: 60)
  -b BALLOTS, --ballots BALLOTS
                        Number of ballots in slot (default: 5)
  -s SENDING, --sending SENDING
                        Number of sending ballots simultaniously (default: 5)
  -cp CONSENSUS_PROTOCOL, --consensus_protocol CONSENSUS_PROTOCOL
                        ex. isaac, instantsend (default: isaac)
```

## Results

### Console
```
● 1521157861.76687407 - __main__ - CRIT - Number of nodes=5 - {}
● 1521157861.76701808 - __main__ - CRIT - Threshold=100 - {}
● 1521157861.76707101 - __main__ - CRIT - Number of ballots in slot=10 - {}
● 1521157861.76711607 - __main__ - CRIT - Number of sending ballots=10 - {}
● 1521157861.76761079 - __main__ - CRIT - 1. Generate_node_names - {}
● 1521157861.76782489 - __main__ - CRIT -    Generate_node_names elapsed time=2.19e-05 sec - {}
● 1521157861.76798701 - __main__ - CRIT - 2. generate_blockchains - {}
● 1521157861.90179992 - __main__ - CRIT -    Generate_blockchains elapsed time=0.0419 sec - {}
● 1521157861.90198302 - __main__ - CRIT - 3. generate_n_messages - {}
● 1521157861.90450692 - __main__ - CRIT -    generate_n_messages elapsed time=0.000335 sec - {}
● 1521157861.90472698 - __main__ - CRIT - 4. send message and run consensus - {}
● 1521157864.49742317 - __main__ - CRIT -    send message and run consensus elapsed time=1.15 sec - {}
● 1521157870.48380589 - __main__ - CRIT - Total Elapsed time=1.2 sec - {}
```

### Verifying In Log
* Performance-test logs

```sh
$ cat /tmp/m.json | jq -S --indent 0 -r 'select(has("action"))' 2> /dev/null | jq -S --indent 0 -r "select(.action==\"performance-test\")" 2> /dev/null
```

> To run this bash script, we need `jq`. To install `jq`, `brew install jq`.

```json
{"Threshold":100,"action":"performance-test","ballots":10,"created":1521683330.650528,"kind":"whole process","logger":"__main__","nodes":5,"sending":10,"timing":"begin"}
{"action":"performance-test","created":1521683330.652823,"kind":"generate node names","logger":"__main__","timing":"begin"}
{"action":"performance-test","created":1521683330.653159,"elapsed_time":"2.19e-05 sec","kind":"generate node names","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521683330.65342,"kind":"generate blockchains","logger":"__main__","timing":"begin"}
{"action":"performance-test","created":1521683330.695604,"elapsed_time":"0.0419 sec","kind":"generate blockchains","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521683330.695868,"kind":"generate n messages","logger":"__main__","timing":"begin"}
{"action":"performance-test","created":1521683330.6965199,"elapsed_time":"0.000335 sec","kind":"generate n messages","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521683330.6967528,"kind":"send message and run consensus","logger":"__main__","timing":"begin"}
{"action":"performance-test","created":1521683331.8470552,"elapsed_time":"1.15 sec","kind":"send message and run consensus","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521683331.8473759,"elapsed_time":"1.2 sec","kind":"whole process","logger":"__main__","timing":"end"}
```

* Filtered by `timing=end` for check just elapsed_time

```sh
cat /tmp/m.json | jq -S --indent 0 -r 'select(has("action"))' 2> /dev/null | jq -S --indent 0 -r "select(.action==\"performance-test\")" 2> /dev/null | jq -S --indent 0 -r "select(.timing==\"end\")" 2> /dev/null
```

```json
{"action":"performance-test","created":1521683330.653159,"elapsed_time":"2.19e-05 sec","kind":"generate node names","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521683330.695604,"elapsed_time":"0.0419 sec","kind":"generate blockchains","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521683330.6965199,"elapsed_time":"0.000335 sec","kind":"generate n messages","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521683331.8470552,"elapsed_time":"1.15 sec","kind":"send message and run consensus","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521683331.8473759,"elapsed_time":"1.2 sec","kind":"whole process","logger":"__main__","timing":"end"}
```

