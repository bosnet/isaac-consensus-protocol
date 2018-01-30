# Makking No Response Server

## Running

```
$ cd examples
$ python run-case.py -log-level info alive-but-not-voting detecting-no-response-nodes/example.yml
● 1517283551.76024795 - __main__ - INFO  - design loaded:
...
● 1517283551.76158786 - consensus - INFO  - [n0] state to IsaacState.INIT - {'node': 'n0'}
● 1517283551.76272988 - consensus - INFO  - [n1] state to IsaacState.INIT - {'node': 'n1'}
● 1517283551.76341987 - consensus - INFO  - [n2] state to IsaacState.INIT - {'node': 'n2'}
● 1517283551.76408505 - consensus - INFO  - [n3] state to IsaacState.INIT - {'node': 'n3'}
● 1517283551.76480508 - consensus - INFO  - [n4] state to IsaacState.INIT - {'node': 'n4'}
● 1517283551.76541114 - consensus - INFO  - [n5] state to IsaacState.INIT - {'node': 'n5'}
...
● 1517283560.28957486 - http.node-unreachable - INFO  - no-response started: choice=9 frequency=10 duration=3 - {'node': 'n5'}
● 1517283564.41218901 - http.node-unreachable - INFO  - no-response ended: last-started=1517283560 elapsed=4 duration=3 - {'node': 'n5'}
● 1517283566.46759510 - http.node-unreachable - INFO  - no-response started: choice=6 frequency=10 duration=3 - {'node': 'n5'}
● 1517283566.46816111 - ping - ERROR - [6] failed to connect to <Node: n5(<Endpoint: http://127.0.0.1:55796?name=n5>)>: 404 Client Error: Not Found for url: http://127.0.0.1:55796/ping - {'node': 'n0'}
...
```

The `detecting-no-response-nodes/example.yml` indicates that 'n5' will be the (sometimes) dead node.

```
...

faulties:
    ...
    n5:
        - case:
            kind: node_unreachable
            frequency: 10
            duration: 3
```
