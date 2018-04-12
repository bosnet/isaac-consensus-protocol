# Quorum Intersection Test In Single Process

## Run Quorum Topology Server Example

```
$ cd examples/cases
$ python run-case.py -log-level error example_conf.yml
```

### example_conf.yml

```
common:
    # consensus: isaac
    network: default_http
    threshold: 60


nodes:
    n0:
        quorum:
            validators:
                - n1
                - n2
                - n3
                - n4
                - n5
                - n6
            threshold: 60

    n1:
        port: 54320
        quorum:
            validators:
                - n0
                - n2
                - n3
                - n7
    n2:
        quorum:
            validators:
                - n0
                - n1
                - n3
                - n7
    n3:
        quorum:
            validators:
                - n0
                - n1
                - n2
                - n5
    n4:
        quorum:
            validators:
                - n1
                - n5
                - n6
    n5:
        quorum:
            validators:
                - n3
                - n4
                - n6
                - n7
    n6:
        quorum:
            validators:
                - n0
                - n4
                - n5
                - n7
    n7:
        quorum:
            validators:
                - n1
                - n2
                - n5
                - n6

messages:
    n1:
        number: 3
        interval: 500
```


### example_faulty.yml

```
common:
    # consensus: isaac
    network: default_http
    threshold: 60


nodes:
    n0:
        quorum:
            validators:
                - n1
                - n2
                - n3
                - n4
                - n5
                - n6
            threshold: 60

    n1:
        port: 54320
        quorum:
            validators:
                - n0
                - n2
                - n3
                - n7
    n2:
        quorum:
            validators:
                - n0
                - n1
                - n3
                - n7
    n3:
        quorum:
            validators:
                - n0
                - n1
                - n2
                - n5
    n4:
        quorum:
            validators:
                - n1
                - n5
                - n6
    n5:
        quorum:
            validators:
                - n3
                - n4
                - n6
                - n7
    n6:
        quorum:
            validators:
                - n0
                - n4
                - n5
                - n7
    n7:
        quorum:
            validators:
                - n1
                - n2
                - n5
                - n6

faulties:
    n0:
        - case:  # multiple cases can be set
            kind: no_voting
            frequency:
                per_consensus: 100  # means, this node will be faulty node in every time
    n1:
        - case:
            kind: state_regression
            frequency: 100  # how often make regressed state within one consensus
            target_nodes:
                - n0
                - n2
    n6:
        - case:
            kind: divergent_voting
            frequency: 100
    n7:
        - case:
            kind: node_unreachable
            frequency: 10  # how often stop response for `/ping`
            duration: 3  # when stopping response, how long will sustain the no response state

messages:
    n1:
        number: 3
        interval: 500
```

## Checking Possibility Of Consensus

You can simply check the given case on whether the consensus is possible or not. Just add `check` at the end of the command line.

```
$ python run-case.py example_conf.yml check
# n0
=========================================================================================
     validators | n0, n1, n2, n3, n4
-----------------------------------------------------------------------------------------
 disabled nodes | -
-----------------------------------------------------------------------------------------
 can consensus? | Yes
=========================================================================================

# n1
=========================================================================================
     validators | n0, n1, n2, n3, n4
-----------------------------------------------------------------------------------------
 disabled nodes | -
-----------------------------------------------------------------------------------------
 can consensus? | Yes
=========================================================================================

# n2
=========================================================================================
     validators | n0, n1, n2, n3, n4
-----------------------------------------------------------------------------------------
 disabled nodes | -
-----------------------------------------------------------------------------------------
 can consensus? | Yes
=========================================================================================

# n3
=========================================================================================
     validators | n0, n1, n2, n3, n4
-----------------------------------------------------------------------------------------
 disabled nodes | -
-----------------------------------------------------------------------------------------
 can consensus? | Yes
=========================================================================================

# n4
=========================================================================================
     validators | n0, n1, n2, n3, n4, n5
-----------------------------------------------------------------------------------------
 disabled nodes | -
-----------------------------------------------------------------------------------------
 can consensus? | Yes
=========================================================================================

# n5
=========================================================================================
     validators | n4, n5, n6, n7, n8
-----------------------------------------------------------------------------------------
 disabled nodes | -
-----------------------------------------------------------------------------------------
 can consensus? | Yes
=========================================================================================

# n6
=========================================================================================
     validators | n4, n5, n6, n7, n8
-----------------------------------------------------------------------------------------
 disabled nodes | -
-----------------------------------------------------------------------------------------
 can consensus? | Yes
=========================================================================================

# n7
=========================================================================================
     validators | n4, n5, n6, n7, n8
-----------------------------------------------------------------------------------------
 disabled nodes | -
-----------------------------------------------------------------------------------------
 can consensus? | Yes
=========================================================================================

# n8
=========================================================================================
     validators | n4, n5, n6, n7, n8
-----------------------------------------------------------------------------------------
 disabled nodes | -
-----------------------------------------------------------------------------------------
 can consensus? | Yes
=========================================================================================
```

## Run Quorum Topology Server and periodically send messages in local

### Safety(Success)

#### Input
```
$ cd examples/cases
$ python run-case-local-socket.py -log-level info example_conf.yml
```
#### Result
```
● 1521070136.32404494 - consensus.state - METR - {
  "node": "n0",
  "messages": [
    "<Message: message_id=74a78e5a27df11e8848a8c85904f3969 data=\"Est-74a78d8827df11e8848a8c85904f3969\">",
    "<Message: message_id=74a7901227df11e8848a8c85904f3969 data=\"Velit-74a78fb827df11e8848a8c85904f3969\">",
    "<Message: message_id=74a7918c27df11e8848a8c85904f3969 data=\"Amet-74a7913427df11e8848a8c85904f3969\">"
  ],
  "faulties": [],
  "quorum": {
    "threshold": 60,
    "validators": [
      "n1",
      "n2",
      "n3",
      "n4",
      "n5",
      "n6"
    ]
  },
  "logger": "consensus.state",
  "created": 1521070136.324045
}
● 1521070136.32452202 - consensus.state - METR - {
  "node": "n1",
  "messages": [
    "<Message: message_id=74a78e5a27df11e8848a8c85904f3969 data=\"Est-74a78d8827df11e8848a8c85904f3969\">",
    "<Message: message_id=74a7901227df11e8848a8c85904f3969 data=\"Velit-74a78fb827df11e8848a8c85904f3969\">",
    "<Message: message_id=74a7918c27df11e8848a8c85904f3969 data=\"Amet-74a7913427df11e8848a8c85904f3969\">"
  ],
  "faulties": [],
  "quorum": {
    "threshold": 60,
    "validators": [
      "n0",
      "n2",
      "n3",
      "n7"
    ]
  },
  "logger": "consensus.state",
  "created": 1521070136.324522
}
● 1521070136.32486987 - consensus.state - METR - {
  "node": "n2",
  "messages": [
    "<Message: message_id=74a78e5a27df11e8848a8c85904f3969 data=\"Est-74a78d8827df11e8848a8c85904f3969\">",
    "<Message: message_id=74a7901227df11e8848a8c85904f3969 data=\"Velit-74a78fb827df11e8848a8c85904f3969\">",
    "<Message: message_id=74a7918c27df11e8848a8c85904f3969 data=\"Amet-74a7913427df11e8848a8c85904f3969\">"
  ],
  "faulties": [],
  "quorum": {
    "threshold": 60,
    "validators": [
      "n0",
      "n1",
      "n3",
      "n7"
    ]
  },
  "logger": "consensus.state",
  "created": 1521070136.3248699
}
● 1521070136.32514095 - consensus.state - METR - {
  "node": "n3",
  "messages": [
    "<Message: message_id=74a78e5a27df11e8848a8c85904f3969 data=\"Est-74a78d8827df11e8848a8c85904f3969\">",
    "<Message: message_id=74a7901227df11e8848a8c85904f3969 data=\"Velit-74a78fb827df11e8848a8c85904f3969\">",
    "<Message: message_id=74a7918c27df11e8848a8c85904f3969 data=\"Amet-74a7913427df11e8848a8c85904f3969\">"
  ],
  "faulties": [],
  "quorum": {
    "threshold": 60,
    "validators": [
      "n0",
      "n1",
      "n2",
      "n5"
    ]
  },
  "logger": "consensus.state",
  "created": 1521070136.325141
}
● 1521070136.32538009 - consensus.state - METR - {
  "node": "n4",
  "messages": [
    "<Message: message_id=74a78e5a27df11e8848a8c85904f3969 data=\"Est-74a78d8827df11e8848a8c85904f3969\">",
    "<Message: message_id=74a7901227df11e8848a8c85904f3969 data=\"Velit-74a78fb827df11e8848a8c85904f3969\">",
    "<Message: message_id=74a7918c27df11e8848a8c85904f3969 data=\"Amet-74a7913427df11e8848a8c85904f3969\">"
  ],
  "faulties": [],
  "quorum": {
    "threshold": 60,
    "validators": [
      "n1",
      "n5",
      "n6"
    ]
  },
  "logger": "consensus.state",
  "created": 1521070136.32538
}
● 1521070136.32561898 - consensus.state - METR - {
  "node": "n5",
  "messages": [
    "<Message: message_id=74a78e5a27df11e8848a8c85904f3969 data=\"Est-74a78d8827df11e8848a8c85904f3969\">",
    "<Message: message_id=74a7901227df11e8848a8c85904f3969 data=\"Velit-74a78fb827df11e8848a8c85904f3969\">",
    "<Message: message_id=74a7918c27df11e8848a8c85904f3969 data=\"Amet-74a7913427df11e8848a8c85904f3969\">"
  ],
  "faulties": [],
  "quorum": {
    "threshold": 60,
    "validators": [
      "n3",
      "n4",
      "n6",
      "n7"
    ]
  },
  "logger": "consensus.state",
  "created": 1521070136.325619
}
● 1521070136.32585406 - consensus.state - METR - {
  "node": "n6",
  "messages": [
    "<Message: message_id=74a78e5a27df11e8848a8c85904f3969 data=\"Est-74a78d8827df11e8848a8c85904f3969\">",
    "<Message: message_id=74a7901227df11e8848a8c85904f3969 data=\"Velit-74a78fb827df11e8848a8c85904f3969\">",
    "<Message: message_id=74a7918c27df11e8848a8c85904f3969 data=\"Amet-74a7913427df11e8848a8c85904f3969\">"
  ],
  "faulties": [],
  "quorum": {
    "threshold": 60,
    "validators": [
      "n0",
      "n4",
      "n5",
      "n7"
    ]
  },
  "logger": "consensus.state",
  "created": 1521070136.325854
}
● 1521070136.32608700 - consensus.state - METR - {
  "node": "n7",
  "messages": [
    "<Message: message_id=74a78e5a27df11e8848a8c85904f3969 data=\"Est-74a78d8827df11e8848a8c85904f3969\">",
    "<Message: message_id=74a7901227df11e8848a8c85904f3969 data=\"Velit-74a78fb827df11e8848a8c85904f3969\">",
    "<Message: message_id=74a7918c27df11e8848a8c85904f3969 data=\"Amet-74a7913427df11e8848a8c85904f3969\">"
  ],
  "faulties": [],
  "quorum": {
    "threshold": 60,
    "validators": [
      "n1",
      "n2",
      "n5",
      "n6"
    ]
  },
  "logger": "consensus.state",
  "created": 1521070136.326087
}
● 1521159724.94809294 - consensus.state - METR - {
  "action": "safety_check",
  "result": "success",
  "logger": "consensus.state",
  "created": 1521159724.948093
}
● 1521159724.94825602 - consensus.state - INFO - [SAFETY] OK! - {}
```
### Safety(Fail)

#### Input
```
$ cd examples/cases
$ python run-case-local-socket.py -log-level info faulty-nodes/alive-but-not-voting/example.yml
```

#### Console Result
```
● 1521159755.30369592 - consensus.state - METR - {
  "node": "n1",
  "messages": [
    "<Message: message_id=1e52c02828b011e899b18c85904f3969 data=\"Etincidunt-1e52bf9428b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c19228b011e899b18c85904f3969 data=\"Labore-1e52c14228b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c2b428b011e899b18c85904f3969 data=\"Quisquam-1e52c27828b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c3c228b011e899b18c85904f3969 data=\"Porro-1e52c38628b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c4da28b011e899b18c85904f3969 data=\"Ipsum-1e52c49428b011e899b18c85904f3969\">"
  ],
  "faulties": [],
  "quorum": {
    "threshold": 60,
    "validators": [
      "n0",
      "n2",
      "n3",
      "n7"
    ]
  },
  "logger": "consensus.state",
  "created": 1521159755.303696
}
● 1521159755.30410910 - consensus.state - METR - {
  "node": "n2",
  "messages": [
    "<Message: message_id=1e52c02828b011e899b18c85904f3969 data=\"Etincidunt-1e52bf9428b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c19228b011e899b18c85904f3969 data=\"Labore-1e52c14228b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c2b428b011e899b18c85904f3969 data=\"Quisquam-1e52c27828b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c3c228b011e899b18c85904f3969 data=\"Porro-1e52c38628b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c4da28b011e899b18c85904f3969 data=\"Ipsum-1e52c49428b011e899b18c85904f3969\">"
  ],
  "faulties": [],
  "quorum": {
    "threshold": 60,
    "validators": [
      "n0",
      "n1",
      "n3",
      "n7"
    ]
  },
  "logger": "consensus.state",
  "created": 1521159755.304109
}
● 1521159755.30453706 - consensus.state - METR - {
  "node": "n3",
  "messages": [
    "<Message: message_id=1e52c02828b011e899b18c85904f3969 data=\"Etincidunt-1e52bf9428b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c19228b011e899b18c85904f3969 data=\"Labore-1e52c14228b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c2b428b011e899b18c85904f3969 data=\"Quisquam-1e52c27828b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c3c228b011e899b18c85904f3969 data=\"Porro-1e52c38628b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c4da28b011e899b18c85904f3969 data=\"Ipsum-1e52c49428b011e899b18c85904f3969\">"
  ],
  "faulties": [],
  "quorum": {
    "threshold": 60,
    "validators": [
      "n0",
      "n1",
      "n2",
      "n5"
    ]
  },
  "logger": "consensus.state",
  "created": 1521159755.304537
}
● 1521159755.30490708 - consensus.state - METR - {
  "node": "n4",
  "messages": [
    "<Message: message_id=1e52c02828b011e899b18c85904f3969 data=\"Etincidunt-1e52bf9428b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c19228b011e899b18c85904f3969 data=\"Labore-1e52c14228b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c2b428b011e899b18c85904f3969 data=\"Quisquam-1e52c27828b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c3c228b011e899b18c85904f3969 data=\"Porro-1e52c38628b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c4da28b011e899b18c85904f3969 data=\"Ipsum-1e52c49428b011e899b18c85904f3969\">"
  ],
  "faulties": [],
  "quorum": {
    "threshold": 60,
    "validators": [
      "n1",
      "n5",
      "n6"
    ]
  },
  "logger": "consensus.state",
  "created": 1521159755.304907
}
● 1521159755.30519700 - consensus.state - METR - {
  "node": "n5",
  "messages": [
    "<Message: message_id=1e52c02828b011e899b18c85904f3969 data=\"Etincidunt-1e52bf9428b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c19228b011e899b18c85904f3969 data=\"Labore-1e52c14228b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c2b428b011e899b18c85904f3969 data=\"Quisquam-1e52c27828b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c3c228b011e899b18c85904f3969 data=\"Porro-1e52c38628b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c4da28b011e899b18c85904f3969 data=\"Ipsum-1e52c49428b011e899b18c85904f3969\">"
  ],
  "faulties": [],
  "quorum": {
    "threshold": 60,
    "validators": [
      "n3",
      "n4",
      "n6",
      "n7"
    ]
  },
  "logger": "consensus.state",
  "created": 1521159755.305197
}
● 1521159755.30547094 - consensus.state - METR - {
  "node": "n6",
  "messages": [
    "<Message: message_id=1e52c02828b011e899b18c85904f3969 data=\"Etincidunt-1e52bf9428b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c19228b011e899b18c85904f3969 data=\"Labore-1e52c14228b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c2b428b011e899b18c85904f3969 data=\"Quisquam-1e52c27828b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c3c228b011e899b18c85904f3969 data=\"Porro-1e52c38628b011e899b18c85904f3969\">",
    "<Message: message_id=1e52c4da28b011e899b18c85904f3969 data=\"Ipsum-1e52c49428b011e899b18c85904f3969\">"
  ],
  "faulties": [],
  "quorum": {
    "threshold": 60,
    "validators": [
      "n0",
      "n4",
      "n5",
      "n7"
    ]
  },
  "logger": "consensus.state",
  "created": 1521159755.305471
}
● 1521159755.30582190 - consensus.state - METR - {
  "node": "n7",
  "messages": [],
  "faulties": [
    [
      "FaultyNodeKind.NoVoting",
      [
        100
      ]
    ]
  ],
  "quorum": {
    "threshold": 60,
    "validators": [
      "n1",
      "n2",
      "n5",
      "n6"
    ]
  },
  "logger": "consensus.state",
  "created": 1521159755.305822
}
● 1521159755.30613303 - consensus.state - METR - {
  "action": "safety_check",
  "result": "fail",
  "info": [
    {
      "message_hash": 3527539,
      "nodes": [
        "n0",
        "n7"
      ],
      "messages": []
    },
    {
      "message_hash": -6901041463367451474,
      "nodes": [
        "n1",
        "n2",
        "n3",
        "n4",
        "n5",
        "n6"
      ],
      "messages": [
        "<Message: message_id=1e52c4da28b011e899b18c85904f3969 data=\"Ipsum-1e52c49428b011e899b18c85904f3969\">",
        "<Message: message_id=1e52c3c228b011e899b18c85904f3969 data=\"Porro-1e52c38628b011e899b18c85904f3969\">",
        "<Message: message_id=1e52c2b428b011e899b18c85904f3969 data=\"Quisquam-1e52c27828b011e899b18c85904f3969\">",
        "<Message: message_id=1e52c19228b011e899b18c85904f3969 data=\"Labore-1e52c14228b011e899b18c85904f3969\">",
        "<Message: message_id=1e52c02828b011e899b18c85904f3969 data=\"Etincidunt-1e52bf9428b011e899b18c85904f3969\">"
      ]
    }
  ],
  "logger": "consensus.state",
  "created": 1521159755.306133
}
● 1521070175.48345590 - consensus.state - INFO - [SAFETY] FAIL! - {}
```
