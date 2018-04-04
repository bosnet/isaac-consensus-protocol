# Verifying Quorum Safety

For detailed process of this issues, please check [BOS-267](https://blockchainos.atlassian.net/browse/BOS-267).

## Quorum Design

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

The `run-case.py` will just launch the servers, which are instructed by the yaml formatted design file, so to make the consensus in quorum, we need run `run-client.py` for send message to server.

```sh
$ cd ./examples/cases
$ python run-case.py -log-level error quorum-safety/double-spending/double-spending.yml
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
