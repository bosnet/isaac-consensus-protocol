# Performance Test

This module is an experimental module to see how the performance of consensus varies according to various cases.
The results obtained from the experiment are as follows.
1. Find optimized slot size according to node numbers.
1. The scalability of how consensus performance degrades with increasing number of nodes.
1. In the same environment, it is to check the performance difference of various consensus algorithms (which are not yet implemented).

>Related issue, please check [BOS-232](https://blockchainos.atlassian.net/browse/BOS-232).

## Running

```sh
$ python examples/experiment/run-performance-by-slot-size.py -log-level error -log-output-metric /tmp/m.json -n 5 -t 100 -b 20 -s 20
```

> Before running this command, make sure you have run `python setup.py develop`.

## Options
```
usage: run-performance-by-slot-size.py [-h] [-verbose]
                                       [-log-level {critical,fatal,error,warn,warning,info,debug}]
                                       [-log-output LOG_OUTPUT]
                                       [-log-output-metric LOG_OUTPUT_METRIC]
                                       [-log-show-line] [-log-no-color]
                                       [-n NODES] [-t THRESHOLD] [-b BALLOTS]
                                       [-s SENDING]

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
```

## Results

### Console
```
● 1521157861.76687407 - __main__ - CRIT - Number of nodes=20 - {}
● 1521157861.76701808 - __main__ - CRIT - Threshold=100 - {}
● 1521157861.76707101 - __main__ - CRIT - Number of ballots in slot=20 - {}
● 1521157861.76711607 - __main__ - CRIT - Number of sending ballots=20 - {}
● 1521157861.76761079 - __main__ - CRIT - 1. Generate_node_names - {}
● 1521157861.76782489 - __main__ - CRIT -    Generate_node_names elapsed time=1e-05 sec - {}
● 1521157861.76798701 - __main__ - CRIT - 2. generate_blockchains - {}
● 1521157861.90179992 - __main__ - CRIT -    Generate_blockchains elapsed time=0.133 sec - {}
● 1521157861.90198302 - __main__ - CRIT - 3. generate_n_ballots_list - {}
● 1521157861.90450692 - __main__ - CRIT -    Generate_n_ballots_list elapsed time=0.00233 sec - {}
● 1521157861.90472698 - __main__ - CRIT - 4. receive INIT state ballots and check state SIGN - {}
● 1521157864.49742317 - __main__ - CRIT -    Receive INIT state ballots and check state SIGN elapsed time=2.59 sec - {}
● 1521157864.49779606 - __main__ - CRIT - 5. receive SIGN state ballots and check state ACCEPT - {}
● 1521157867.44960999 - __main__ - CRIT -    Receive SIGN state ballots and check state ACCEPT elapsed time=2.95 sec - {}
● 1521157867.44995880 - __main__ - CRIT - 6. receive ACCEPT ballots and check state ALL_CONFIRM - {}
● 1521157870.47692013 - __main__ - CRIT -    Receive ACCEPT state ballots and check state ALL_CONFIRM elapsed time=3.03 sec - {}
● 1521157870.48380589 - __main__ - CRIT - Total Elapsed time=8.72 sec - {}
```

### Verifying In Log
* Performance-test logs

```sh
$ cat /tmp/m.json | jq -S --indent 0 -r 'select(has("action"))' 2> /dev/null | jq -S --indent 0 -r "select(.action==\"performance-test\")" 2> /dev/null
```

> To run this bash script, we need `jq`. To install `jq`, `brew install jq`.

```json
{"Threshold":100,"action":"performance-test","ballots":20,"created":1521157861.7671921,"kind":"whole process","logger":"__main__","nodes":20,"sending":20,"timing":"begin"}
{"action":"performance-test","created":1521157861.7676768,"kind":"generate node names","logger":"__main__","timing":"begin"}
{"action":"performance-test","created":1521157861.7678778,"elapsed_time":"1e-05 sec","kind":"generate node names","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521157861.768034,"kind":"generate blockchains","logger":"__main__","timing":"begin"}
{"action":"performance-test","created":1521157861.901879,"elapsed_time":"0.133 sec","kind":"generate blockchains","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521157861.902058,"kind":"generate n ballot list","logger":"__main__","timing":"begin"}
{"action":"performance-test","created":1521157861.904602,"elapsed_time":"0.00233 sec","kind":"generate n ballot list","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521157861.9047759,"kind":"receive INIT state and check state SIGN","logger":"__main__","timing":"begin"}
{"action":"performance-test","created":1521157864.497587,"elapsed_time":"2.59 sec","kind":"receive INIT state and check state SIGN","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521157864.497868,"kind":"receive SIGN state and check state ACCEPT","logger":"__main__","timing":"begin"}
{"action":"performance-test","created":1521157867.4497259,"elapsed_time":"2.95 sec","kind":"receive SIGN state and check state ACCEPT","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521157867.450028,"kind":"receive ACCEPT ballots and check state ALL_CONFIRM","logger":"__main__","timing":"begin"}
{"action":"performance-test","created":1521157870.477002,"elapsed_time":"3.03 sec","kind":"receive ACCEPT ballots and check state ALL_CONFIRM","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521157870.483937,"elapsed_time":"8.72 sec","kind":"whole process","logger":"__main__","timing":"end"}
```

* Filtered by `timing=end` for check just elapsed_time

```sh
cat /tmp/m.json | jq -S --indent 0 -r 'select(has("action"))' 2> /dev/null | jq -S --indent 0 -r "select(.action==\"performance-test\")" 2> /dev/null | jq -S --indent 0 -r "select(.timing==\"end\")" 2> /dev/null
```

```json
{"action":"performance-test","created":1521157861.7678778,"elapsed_time":"1e-05 sec","kind":"generate node names","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521157861.901879,"elapsed_time":"0.133 sec","kind":"generate blockchains","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521157861.904602,"elapsed_time":"0.00233 sec","kind":"generate n ballot list","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521157864.497587,"elapsed_time":"2.59 sec","kind":"receive INIT state and check state SIGN","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521157867.4497259,"elapsed_time":"2.95 sec","kind":"receive SIGN state and check state ACCEPT","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521157870.477002,"elapsed_time":"3.03 sec","kind":"receive ACCEPT ballots and check state ALL_CONFIRM","logger":"__main__","timing":"end"}
{"action":"performance-test","created":1521157870.483937,"elapsed_time":"8.72 sec","kind":"whole process","logger":"__main__","timing":"end"}
```

