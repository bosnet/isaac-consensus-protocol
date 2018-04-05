# Verifying Quorum Safety: Double Spending

For detailed process of this issues, please check [BOS-267](https://blockchainos.atlassian.net/browse/BOS-267).

## Running

The `run-case.py` will just launch the servers that are constructed by the yaml formatted design file. To verify a message through consensus, we need to run `run-client.py` to send message to server.


Substitute the `<DESIGN_FILE>.yml` to run a specific case for double spending
```sh
$ cd ./examples/cases
$ python run-case.py -log-level error -log-output-metric /tmp/double.json quorum-safety/double-spending/<DESIGN_FILE>.yml
```


and then send two messages to other nodes at the same time
```sh
$ python ./scripts/run-client.py -id 104 -i localhost -p 54320 -m message
$ python ./scripts/run-client.py -id 104 -i localhost -p 54321 -m different_message
```

or

```sh
$ send-message.py -same-message-id http://localhost:54320?m=1  http://localhost:54321?m=1
```

> The port `54320` is already assigned port by the design file for the node 'n1' and the port `54321` is assigned as node 'n10'.

## Quorum Design: `double-spending.yml`

* We have 4 quorums.
* Four quorums are loosely linked by common nodes.
    * Commons: n3 n6 n9
    * q0:
      - validators: n0 n1 n2 n3
    * q1:
      - validators: n3 n4 n5 n6
    * q2:
      - validators: n6 n7 n8 n9
    * q3:
      - validators: n9 n10 n11 n12

## Running `double-spending.yml`

Substitute the `<DESIGN_FILE>.yml` to `double-spending.yml` in the above example

### Verifying in Browser

Open your browser and connect to http://localhost:54320/ for n1.
Then, you will see these results in the browser.

```json
{
 "version": "0.8.1",
 "blockchain": {
  "node": {
   "name": "n1",
   "endpoint": "http://127.0.0.1:54320?name=n1"
  },
  "consensus": {
   "validator_candidates": [
    {
     "name": "n0",
     "endpoint": "http://127.0.0.1:50458?name=n0"
    },
    {
     "name": "n2",
     "endpoint": "http://127.0.0.1:50459?name=n2"
    },
    {
     "name": "n3",
     "endpoint": "http://127.0.0.1:50460?name=n3"
    }
   ],
   "threshold": 60,
   "messages": [
    {
     "message_id": "104",
     "data": "message"
    }
   ]
  }
 }
}
```

And Connect to http://localhost:54321/ for n10. Then, you will see these results in the browser.

```json
{
 "version": "0.8.1",
 "blockchain": {
  "node": {
   "name": "n1",
   "endpoint": "http://127.0.0.1:54320?name=n1"
  },
  "consensus": {
   "validator_candidates": [
    {
     "name": "n0",
     "endpoint": "http://127.0.0.1:50458?name=n0"
    },
    {
     "name": "n2",
     "endpoint": "http://127.0.0.1:50459?name=n2"
    },
    {
     "name": "n3",
     "endpoint": "http://127.0.0.1:50460?name=n3"
    }
   ],
   "threshold": 60,
   "messages": [
    {
     "message_id": "104",
     "data": "different_message"
    }
   ]
  }
 }
}
```

Look at the "messages" carefully. Two nodes n1 and n10 got the messages, which has same message_id, but different data. This means that the safety is not satisfied.



## Quorum Design: `double-spending-many-extras.yml`

* We have 2 quorums.
* 2 quorums share two common nodes.
    * Commons: n4 n5
    * q0:
      - validators: n0 n1 n2 n3 n4 n5
    * q1:
      - validators: n4 n5 n6 n7 n8 n9

## Running `double-spending-many-extras.yml`

Substitute the `<DESIGN_FILE>.yml` to `double-spending-many-extras.yml` in the above example

### Verifying in Browser

Open your browser and connect to http://localhost:54320/ for n1.
Then, you will see these results in the browser.

```json
{
 "version": "0.8.1",
 "blockchain": {
  "node": {
   "name": "n1",
   "endpoint": "http://127.0.0.1:54320?name=n1"
  },
  "consensus": {
   "validator_candidates": [
    {
     "name": "n0",
     "endpoint": "http://127.0.0.1:54765?name=n0"
    },
    {
     "name": "n2",
     "endpoint": "http://127.0.0.1:54766?name=n2"
    },
    {
     "name": "n3",
     "endpoint": "http://127.0.0.1:54767?name=n3"
    },
    {
     "name": "n4",
     "endpoint": "http://127.0.0.1:54768?name=n4"
    },
    {
     "name": "n5",
     "endpoint": "http://127.0.0.1:54769?name=n5"
    }
   ],
   "threshold": 60,
   "messages": [
    {
     "message_id": "864296d037c211e8b3708c8590553c89",
     "data": "Modi-8646efc837c211e8b3708c8590553c89"
    }
   ]
  }
 }
}
```

And Connect to http://localhost:54321/ for n10. Then, you will see these results in the browser.

```json
{
 "version": "0.8.1",
 "blockchain": {
  "node": {
   "name": "n9",
   "endpoint": "http://127.0.0.1:54321?name=n9"
  },
  "consensus": {
   "validator_candidates": [
    {
     "name": "n4",
     "endpoint": "http://127.0.0.1:54768?name=n4"
    },
    {
     "name": "n5",
     "endpoint": "http://127.0.0.1:54769?name=n5"
    },
    {
     "name": "n6",
     "endpoint": "http://127.0.0.1:54770?name=n6"
    },
    {
     "name": "n7",
     "endpoint": "http://127.0.0.1:54771?name=n7"
    },
    {
     "name": "n8",
     "endpoint": "http://127.0.0.1:54772?name=n8"
    }
   ],
   "threshold": 60,
   "messages": [
    {
     "message_id": "864296d037c211e8b3708c8590553c89",
     "data": "Dolor-864722ae37c211e8b3708c8590553c89"
    }
   ]
  }
 }
}
```

Look at the "messages" carefully. Two nodes n1 and n9 got the messages, which has same message_id, but different data. This means that safety is not satisfied.



