# Quorum Intersection Test In Single Process

## Run Quorum Topology Server and periodically send messages in local

```
$ cd examples/cases
$ python run-case-local-socket.py -log-level error example_conf.json
or
$ python run-case-local-socket.py -log-level error example_conf.yml
```

## Run Quorum Topology Server Example

```
$ cd examples/cases
$ python run-case.py -log-level error example_conf.json
or
$ python run-case.py -log-level error example_conf.yml
```

## Input Json File Format

```
{
    "common":
    {
        "network": string
    },
    "nodes":
    {
        "Node Name":
        {
            "threshold": integer,
            "faulty_percent": integer,
            "faulty_kind": string
        },
        "Node Name": {} // default threshold 51
    },
    "groups": // The left operand and the right operand are bidirectional validators
    {
        "Group Name":
            [
                "Node Name",
                "Node Name"
            ],
        "Group Name":
            [
                "Node Name",
                "Node Name"
            ]
    },
    "binary_link": // The left operand and the right operand are bidirectional validators
    [
        [
          ["Node Name"], // left operand
          ["Node Name", "Node Name"] // right operand
        ],
        [
          ["Node Name"], // left operand
          ["Node Name", "Node Name"] // right operand
        ]
    ],
    "unary_link": // The left operand and the right operand are unidirectional validators
    [
        [ ["Node Name"], ["Node Name"] ]
    ],
    "messages":
    {
        "Node Name":                    // Node name that to send messages
        {
            "number": integer,          // The number of messages
            "interval": integer         // Interval between messages(ms)
        }
    }
}
```

### example_conf.json
```
{
    "common":
        {
            "network": "default_http",
            "threshold": 60
        },

    "nodes":
    {
        "n1":
        {
            "threshold": 80
        },
        "n2":
        {
            "threshold": 80
        },
        "n3":
        {
            "threshold": 80
        },
        "n4":
        {
        },
        "n5":
        {
            "threshold": 80
        },
        "n6":
        {
            "threshold": 51
        },
        "n7":
        {
            "threshold": 51
        },
        "n8":
        {
            "threshold": 51
        },
        "n9":
        {
        }
    },

    "groups":
    {
        "g1": ["n1", "n2", "n3"],
        "g2": ["n4", "n5", "n6", "n7"]
    },

    "binary_link":
    [
        [ ["n8"], ["n3", "n4"] ],
        [ ["n9"], ["n3", "n6"] ]
    ],
    
    "unary_link":
    [
        [ ["n9"], ["n1"] ]
    ],
    
    "messages":
    {
        "n1":
        {
            "number": 5,
            "interval": 500
        }
    }
}
```

### example_faulty.json
```
{

    "common":
        {
            "network": "default_http",
            "threshold": 60
        },

    "nodes":
    {

        "n1":
        {
            "threshold": 80,
            "faulty_kind": "no_voting",
            "faulty_percent":
            {
                "per_consensus": 100
            }
        },
        "n2":
        {
            "threshold": 80,
            "faulty_kind": "duplicated_message_sent",
            "faulty_percent": 1
        },
        "n3":
        {
            "threshold": 80,
            "faulty_kind": "node_unreachable",
            "faulty_percent": 20,
            "duration": 3
        },
        "n4":
        {
            "faulty_kind": "divergent_voting",
            "faulty_percent": 1
        },
        "n5":
        {
            "threshold": 80,
            "faulty_kind": "state_regression",
            "faulty_percent": 1,
            "target_nodes" : ["n0", "n2"]
        },
        "n6":
        {
            "threshold": 51
        },
        "n7":
        {
            "threshold": 51
        },
        "n8":
        {
            "threshold": 51
        },
        "n9":
        {
        }
    },

    "groups":
    {
        "g1": ["n1", "n2", "n3"],
        "g2": ["n4", "n5", "n6", "n7"]
    },

    "binary_link":
    [
        [ ["n8"], ["n3", "n4"] ],
        [ ["n9"], ["n3", "n6"] ]
    ],
    
    "unary_link":
    [
        [ ["n9"], ["n1"] ]
    ],
    
    "messages":
    {
        "n1":
        {
            "number": 5,
            "interval": 500
        }
    }
}
```