# Verifying Quroum Safety

For detailed process of this issues, please check [BOS-187](https://blockchainos.atlassian.net/browse/BOS-187).

## Running

The `run-case.py` will just launch the servers, which are instructed by design yaml file, so to occur the consensus, we need to run `run-client.py` to send message to server.

```sh
$ cd ./examples/cases
```

## Quorum Design

* We have 2 quorums
* Each quorum satisfies,
    - has number of nodes for fault tolderance at least
    - has number of common nodes for safety
    - has number of extra nodes for liveness

## None Faulty Nodes: `safe-common-1.yml`

```sh
$ python run-case.py -log-level error -log-output-metric /tmp/metric.json quorum-safety/safe-common-1.yml
```

and then send message
```sh
$ python run-client-new.py http://localhost:54320
```

> The `54320` is already assigned port by the design file for the node, 'n1'.

### Verifying In Logs

* the important metric messages in all nodes
```sh
$ for i in $(seq 0 8)
do
    echo '["------------------------------------"]'
    cat /tmp/metric.json | jq -S --indent 0 -r 'select(has("action"))' 2> /dev/null | jq -S --indent 0 -r "select(.node==\"n$i\")" 2> /dev/null
done
```

> To run this bash script, we need `jq`. To install `jq`, `brew install jq`.

```json
["------------------------------------"]
{"action":"change-state","created":1519102461.585979,"logger":"consensus","node":"n0","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519102461.586428,"logger":"consensus","node":"n0","target":"n0","validators":["n0"]}
{"action":"connected","created":1519102463.699223,"logger":"consensus","node":"n0","target":"n1","validators":["n0","n1"]}
{"action":"connected","created":1519102463.733474,"logger":"consensus","node":"n0","target":"n2","validators":["n0","n1","n2"]}
{"action":"connected","created":1519102463.775525,"logger":"consensus","node":"n0","target":"n3","validators":["n0","n1","n2","n3"]}
{"action":"connected","created":1519102463.827187,"logger":"consensus","node":"n0","target":"n4","validators":["n0","n1","n2","n3","n4"]}
{"action":"change-state","created":1519102465.844577,"logger":"consensus","node":"n0","state":{"after":"INIT","before":"INIT"},"validators":["n0","n1","n2","n3","n4"]}
{"action":"change-state","created":1519102470.7674398,"logger":"consensus","node":"n0","state":{"after":"SIGN","before":"INIT"},"validators":["n0","n1","n2","n3","n4"]}
{"action":"change-state","created":1519102470.841517,"logger":"consensus","node":"n0","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n0","n1","n2","n3","n4"]}
{"action":"change-state","created":1519102470.902197,"logger":"consensus","node":"n0","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n0","n1","n2","n3","n4"]}
{"action":"save-message","created":1519102470.905432,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n0"}
["------------------------------------"]
{"action":"change-state","created":1519102461.646296,"logger":"consensus","node":"n1","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519102461.646616,"logger":"consensus","node":"n1","target":"n1","validators":["n1"]}
{"action":"connected","created":1519102463.700119,"logger":"consensus","node":"n1","target":"n0","validators":["n1","n0"]}
{"action":"connected","created":1519102463.7441962,"logger":"consensus","node":"n1","target":"n2","validators":["n1","n0","n2"]}
{"action":"connected","created":1519102463.785931,"logger":"consensus","node":"n1","target":"n3","validators":["n1","n0","n2","n3"]}
{"action":"connected","created":1519102463.845712,"logger":"consensus","node":"n1","target":"n4","validators":["n1","n0","n2","n3","n4"]}
{"action":"change-state","created":1519102465.856184,"logger":"consensus","node":"n1","state":{"after":"INIT","before":"INIT"},"validators":["n1","n0","n2","n3","n4"]}
{"action":"receive-message","created":1519102469.6791198,"logger":"blockchain","messge":"21bc87a815fa11e880fa8c85903262b4","node":"n1","state":"INIT"}
{"action":"change-state","created":1519102470.789473,"logger":"consensus","node":"n1","state":{"after":"SIGN","before":"INIT"},"validators":["n1","n0","n2","n3","n4"]}
{"action":"change-state","created":1519102470.860277,"logger":"consensus","node":"n1","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n1","n0","n2","n3","n4"]}
{"action":"change-state","created":1519102470.89686,"logger":"consensus","node":"n1","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n1","n0","n2","n3","n4"]}
{"action":"save-message","created":1519102470.902257,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n1"}
["------------------------------------"]
{"action":"change-state","created":1519102461.647614,"logger":"consensus","node":"n2","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519102461.6478999,"logger":"consensus","node":"n2","target":"n2","validators":["n2"]}
{"action":"connected","created":1519102463.713223,"logger":"consensus","node":"n2","target":"n0","validators":["n2","n0"]}
{"action":"connected","created":1519102463.773998,"logger":"consensus","node":"n2","target":"n1","validators":["n2","n0","n1"]}
{"action":"connected","created":1519102463.806278,"logger":"consensus","node":"n2","target":"n3","validators":["n2","n0","n1","n3"]}
{"action":"connected","created":1519102463.863439,"logger":"consensus","node":"n2","target":"n4","validators":["n2","n0","n1","n3","n4"]}
{"action":"change-state","created":1519102465.882285,"logger":"consensus","node":"n2","state":{"after":"INIT","before":"INIT"},"validators":["n2","n0","n1","n3","n4"]}
{"action":"change-state","created":1519102470.777078,"logger":"consensus","node":"n2","state":{"after":"SIGN","before":"INIT"},"validators":["n2","n0","n1","n3","n4"]}
{"action":"change-state","created":1519102470.823013,"logger":"consensus","node":"n2","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n2","n0","n1","n3","n4"]}
{"action":"change-state","created":1519102470.881957,"logger":"consensus","node":"n2","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n2","n0","n1","n3","n4"]}
{"action":"save-message","created":1519102470.8822248,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n2"}
["------------------------------------"]
{"action":"change-state","created":1519102461.649524,"logger":"consensus","node":"n3","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519102461.649719,"logger":"consensus","node":"n3","target":"n3","validators":["n3"]}
{"action":"connected","created":1519102463.709116,"logger":"consensus","node":"n3","target":"n0","validators":["n3","n0"]}
{"action":"connected","created":1519102463.779148,"logger":"consensus","node":"n3","target":"n1","validators":["n3","n0","n1"]}
{"action":"connected","created":1519102463.842498,"logger":"consensus","node":"n3","target":"n2","validators":["n3","n0","n1","n2"]}
{"action":"connected","created":1519102463.865021,"logger":"consensus","node":"n3","target":"n4","validators":["n3","n0","n1","n2","n4"]}
{"action":"change-state","created":1519102465.888594,"logger":"consensus","node":"n3","state":{"after":"INIT","before":"INIT"},"validators":["n3","n0","n1","n2","n4"]}
{"action":"change-state","created":1519102470.782075,"logger":"consensus","node":"n3","state":{"after":"SIGN","before":"INIT"},"validators":["n3","n0","n1","n2","n4"]}
{"action":"change-state","created":1519102470.831275,"logger":"consensus","node":"n3","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n3","n0","n1","n2","n4"]}
{"action":"change-state","created":1519102470.905301,"logger":"consensus","node":"n3","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n3","n0","n1","n2","n4"]}
{"action":"save-message","created":1519102470.9087481,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n3"}
["------------------------------------"]
{"action":"change-state","created":1519102461.6508968,"logger":"consensus","node":"n4","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519102461.651306,"logger":"consensus","node":"n4","target":"n4","validators":["n4"]}
{"action":"connected","created":1519102463.708435,"logger":"consensus","node":"n4","target":"n0","validators":["n4","n0"]}
{"action":"connected","created":1519102463.74839,"logger":"consensus","node":"n4","target":"n1","validators":["n4","n0","n1"]}
{"action":"connected","created":1519102463.7811258,"logger":"consensus","node":"n4","target":"n2","validators":["n4","n0","n1","n2"]}
{"action":"connected","created":1519102463.834922,"logger":"consensus","node":"n4","target":"n3","validators":["n4","n0","n1","n2","n3"]}
{"action":"connected","created":1519102463.8659232,"logger":"consensus","node":"n4","target":"n5","validators":["n4","n0","n1","n2","n3","n5"]}
{"action":"change-state","created":1519102465.8907049,"logger":"consensus","node":"n4","state":{"after":"INIT","before":"INIT"},"validators":["n4","n0","n1","n2","n3","n5"]}
{"action":"change-state","created":1519102470.9057841,"logger":"consensus","node":"n4","state":{"after":"SIGN","before":"INIT"},"validators":["n4","n0","n1","n2","n3","n5"]}
{"action":"change-state","created":1519102470.9621298,"logger":"consensus","node":"n4","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n4","n0","n1","n2","n3","n5"]}
{"action":"change-state","created":1519102470.979887,"logger":"consensus","node":"n4","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n4","n0","n1","n2","n3","n5"]}
{"action":"save-message","created":1519102470.980119,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n4"}
["------------------------------------"]
{"action":"change-state","created":1519102461.652878,"logger":"consensus","node":"n5","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519102461.6530602,"logger":"consensus","node":"n5","target":"n5","validators":["n5"]}
{"action":"connected","created":1519102463.712703,"logger":"consensus","node":"n5","target":"n4","validators":["n5","n4"]}
{"action":"connected","created":1519102463.7708118,"logger":"consensus","node":"n5","target":"n6","validators":["n5","n4","n6"]}
{"action":"connected","created":1519102463.798325,"logger":"consensus","node":"n5","target":"n7","validators":["n5","n4","n6","n7"]}
{"action":"connected","created":1519102463.863799,"logger":"consensus","node":"n5","target":"n8","validators":["n5","n4","n6","n7","n8"]}
{"action":"change-state","created":1519102465.890529,"logger":"consensus","node":"n5","state":{"after":"INIT","before":"INIT"},"validators":["n5","n4","n6","n7","n8"]}
{"action":"change-state","created":1519102472.7478871,"logger":"consensus","node":"n5","state":{"after":"SIGN","before":"INIT"},"validators":["n5","n4","n6","n7","n8"]}
{"action":"change-state","created":1519102472.777222,"logger":"consensus","node":"n5","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n5","n4","n6","n7","n8"]}
{"action":"change-state","created":1519102472.813143,"logger":"consensus","node":"n5","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n5","n4","n6","n7","n8"]}
{"action":"save-message","created":1519102472.81517,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n5"}
["------------------------------------"]
{"action":"change-state","created":1519102461.653923,"logger":"consensus","node":"n6","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519102461.6542258,"logger":"consensus","node":"n6","target":"n6","validators":["n6"]}
{"action":"connected","created":1519102463.7009332,"logger":"consensus","node":"n6","target":"n4","validators":["n6","n4"]}
{"action":"connected","created":1519102463.739994,"logger":"consensus","node":"n6","target":"n5","validators":["n6","n4","n5"]}
{"action":"connected","created":1519102463.786152,"logger":"consensus","node":"n6","target":"n7","validators":["n6","n4","n5","n7"]}
{"action":"connected","created":1519102463.849814,"logger":"consensus","node":"n6","target":"n8","validators":["n6","n4","n5","n7","n8"]}
{"action":"change-state","created":1519102465.860403,"logger":"consensus","node":"n6","state":{"after":"INIT","before":"INIT"},"validators":["n6","n4","n5","n7","n8"]}
{"action":"change-state","created":1519102472.7597172,"logger":"consensus","node":"n6","state":{"after":"SIGN","before":"INIT"},"validators":["n6","n4","n5","n7","n8"]}
{"action":"change-state","created":1519102472.7901618,"logger":"consensus","node":"n6","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n6","n4","n5","n7","n8"]}
{"action":"change-state","created":1519102473.820819,"logger":"consensus","node":"n6","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n6","n4","n5","n7","n8"]}
{"action":"save-message","created":1519102473.821167,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n6"}
["------------------------------------"]
{"action":"change-state","created":1519102461.655592,"logger":"consensus","node":"n7","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519102461.655793,"logger":"consensus","node":"n7","target":"n7","validators":["n7"]}
{"action":"connected","created":1519102463.716434,"logger":"consensus","node":"n7","target":"n4","validators":["n7","n4"]}
{"action":"connected","created":1519102463.803999,"logger":"consensus","node":"n7","target":"n5","validators":["n7","n4","n5"]}
{"action":"connected","created":1519102463.8573399,"logger":"consensus","node":"n7","target":"n6","validators":["n7","n4","n5","n6"]}
{"action":"connected","created":1519102463.887358,"logger":"consensus","node":"n7","target":"n8","validators":["n7","n4","n5","n6","n8"]}
{"action":"change-state","created":1519102465.896629,"logger":"consensus","node":"n7","state":{"after":"INIT","before":"INIT"},"validators":["n7","n4","n5","n6","n8"]}
{"action":"change-state","created":1519102472.762927,"logger":"consensus","node":"n7","state":{"after":"SIGN","before":"INIT"},"validators":["n7","n4","n5","n6","n8"]}
{"action":"change-state","created":1519102472.7956119,"logger":"consensus","node":"n7","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n7","n4","n5","n6","n8"]}
{"action":"change-state","created":1519102472.826307,"logger":"consensus","node":"n7","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n7","n4","n5","n6","n8"]}
{"action":"save-message","created":1519102472.826508,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n7"}
["------------------------------------"]
{"action":"change-state","created":1519102461.656652,"logger":"consensus","node":"n8","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519102461.656988,"logger":"consensus","node":"n8","target":"n8","validators":["n8"]}
{"action":"connected","created":1519102463.708035,"logger":"consensus","node":"n8","target":"n4","validators":["n8","n4"]}
{"action":"connected","created":1519102463.7623858,"logger":"consensus","node":"n8","target":"n5","validators":["n8","n4","n5"]}
{"action":"connected","created":1519102463.803669,"logger":"consensus","node":"n8","target":"n6","validators":["n8","n4","n5","n6"]}
{"action":"connected","created":1519102463.855357,"logger":"consensus","node":"n8","target":"n7","validators":["n8","n4","n5","n6","n7"]}
{"action":"change-state","created":1519102465.86005,"logger":"consensus","node":"n8","state":{"after":"INIT","before":"INIT"},"validators":["n8","n4","n5","n6","n7"]}
{"action":"change-state","created":1519102473.7496068,"logger":"consensus","node":"n8","state":{"after":"SIGN","before":"INIT"},"validators":["n8","n4","n5","n6","n7"]}
{"action":"change-state","created":1519102473.765661,"logger":"consensus","node":"n8","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n8","n4","n5","n6","n7"]}
{"action":"change-state","created":1519102473.784415,"logger":"consensus","node":"n8","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n8","n4","n5","n6","n7"]}
{"action":"save-message","created":1519102473.784682,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n8"}```
```

* filtered the `save-message` actions
```sh
$ cat /tmp/metric.json | jq -S --indent 0 -r 'select(.action=="save-message")' 2> /dev/null
```

```json
{"action":"save-message","created":1519102470.905432,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n0"}
{"action":"save-message","created":1519102470.902257,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n1"}
{"action":"save-message","created":1519102470.8822248,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n2"}
{"action":"save-message","created":1519102470.9087481,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n3"}
{"action":"save-message","created":1519102470.980119,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n4"}
{"action":"save-message","created":1519102472.81517,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n5"}
{"action":"save-message","created":1519102473.821167,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n6"}
{"action":"save-message","created":1519102472.826508,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n7"}
{"action":"save-message","created":1519102473.784682,"logger":"consensus","message":"21bc87a815fa11e880fa8c85903262b4","node":"n8"}
```

This will show the all the nodes saved the same message(`21bc87a815fa11e880fa8c85903262b4`) and reached the `ALLCONFIRM` state.

## One Faulty Nodes: `safe-common-1-is-faulty.yml`

* the important metric messages in all nodes
```json
["------------------------------------"]
{"action":"change-state","created":1519105361.199402,"logger":"consensus","node":"n0","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105361.200086,"logger":"consensus","node":"n0","target":"n0","validators":["n0"]}
{"action":"connected","created":1519105363.431763,"logger":"consensus","node":"n0","target":"n1","validators":["n0","n1"]}
{"action":"connected","created":1519105363.472251,"logger":"consensus","node":"n0","target":"n2","validators":["n0","n1","n2"]}
{"action":"connected","created":1519105363.5395951,"logger":"consensus","node":"n0","target":"n3","validators":["n0","n1","n2","n3"]}
{"action":"connected","created":1519105363.594304,"logger":"consensus","node":"n0","target":"n4","validators":["n0","n1","n2","n3","n4"]}
{"action":"change-state","created":1519105365.6143382,"logger":"consensus","node":"n0","state":{"after":"INIT","before":"INIT"},"validators":["n0","n1","n2","n3","n4"]}
{"action":"change-state","created":1519105370.474611,"logger":"consensus","node":"n0","state":{"after":"SIGN","before":"INIT"},"validators":["n0","n1","n2","n3","n4"]}
{"action":"change-state","created":1519105370.522669,"logger":"consensus","node":"n0","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n0","n1","n2","n3","n4"]}
{"action":"change-state","created":1519105370.562321,"logger":"consensus","node":"n0","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n0","n1","n2","n3","n4"]}
{"action":"save-message","created":1519105370.562658,"logger":"consensus","message":"e2928082160011e8bc6d0050b68fda61","node":"n0"}
["------------------------------------"]
{"action":"change-state","created":1519105361.329414,"logger":"consensus","node":"n1","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105361.3297951,"logger":"consensus","node":"n1","target":"n1","validators":["n1"]}
{"action":"connected","created":1519105363.472673,"logger":"consensus","node":"n1","target":"n0","validators":["n1","n0"]}
{"action":"connected","created":1519105363.5344179,"logger":"consensus","node":"n1","target":"n2","validators":["n1","n0","n2"]}
{"action":"connected","created":1519105363.598033,"logger":"consensus","node":"n1","target":"n3","validators":["n1","n0","n2","n3"]}
{"action":"connected","created":1519105363.663669,"logger":"consensus","node":"n1","target":"n4","validators":["n1","n0","n2","n3","n4"]}
{"action":"change-state","created":1519105365.670142,"logger":"consensus","node":"n1","state":{"after":"INIT","before":"INIT"},"validators":["n1","n0","n2","n3","n4"]}
{"action":"receive-message","created":1519105369.4033651,"logger":"blockchain","messge":"e2928082160011e8bc6d0050b68fda61","node":"n1","state":"INIT"}
{"action":"change-state","created":1519105370.505545,"logger":"consensus","node":"n1","state":{"after":"SIGN","before":"INIT"},"validators":["n1","n0","n2","n3","n4"]}
{"action":"change-state","created":1519105370.554476,"logger":"consensus","node":"n1","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n1","n0","n2","n3","n4"]}
{"action":"change-state","created":1519105370.605854,"logger":"consensus","node":"n1","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n1","n0","n2","n3","n4"]}
{"action":"save-message","created":1519105370.606077,"logger":"consensus","message":"e2928082160011e8bc6d0050b68fda61","node":"n1"}
["------------------------------------"]
{"action":"change-state","created":1519105361.330902,"logger":"consensus","node":"n2","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105361.331192,"logger":"consensus","node":"n2","target":"n2","validators":["n2"]}
{"action":"connected","created":1519105363.47048,"logger":"consensus","node":"n2","target":"n0","validators":["n2","n0"]}
{"action":"connected","created":1519105363.5231922,"logger":"consensus","node":"n2","target":"n1","validators":["n2","n0","n1"]}
{"action":"connected","created":1519105363.586924,"logger":"consensus","node":"n2","target":"n3","validators":["n2","n0","n1","n3"]}
{"action":"connected","created":1519105363.615988,"logger":"consensus","node":"n2","target":"n4","validators":["n2","n0","n1","n3","n4"]}
{"action":"change-state","created":1519105365.6285682,"logger":"consensus","node":"n2","state":{"after":"INIT","before":"INIT"},"validators":["n2","n0","n1","n3","n4"]}
{"action":"change-state","created":1519105370.501066,"logger":"consensus","node":"n2","state":{"after":"SIGN","before":"INIT"},"validators":["n2","n0","n1","n3","n4"]}
{"action":"change-state","created":1519105370.5468411,"logger":"consensus","node":"n2","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n2","n0","n1","n3","n4"]}
{"action":"change-state","created":1519105370.596576,"logger":"consensus","node":"n2","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n2","n0","n1","n3","n4"]}
{"action":"save-message","created":1519105370.599231,"logger":"consensus","message":"e2928082160011e8bc6d0050b68fda61","node":"n2"}
["------------------------------------"]
{"action":"change-state","created":1519105361.332097,"logger":"consensus","node":"n3","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105361.332278,"logger":"consensus","node":"n3","target":"n3","validators":["n3"]}
{"action":"connected","created":1519105363.4772868,"logger":"consensus","node":"n3","target":"n0","validators":["n3","n0"]}
{"action":"connected","created":1519105363.546315,"logger":"consensus","node":"n3","target":"n1","validators":["n3","n0","n1"]}
{"action":"connected","created":1519105363.592036,"logger":"consensus","node":"n3","target":"n2","validators":["n3","n0","n1","n2"]}
{"action":"connected","created":1519105363.647337,"logger":"consensus","node":"n3","target":"n4","validators":["n3","n0","n1","n2","n4"]}
{"action":"change-state","created":1519105365.656429,"logger":"consensus","node":"n3","state":{"after":"INIT","before":"INIT"},"validators":["n3","n0","n1","n2","n4"]}
{"action":"change-state","created":1519105370.484998,"logger":"consensus","node":"n3","state":{"after":"SIGN","before":"INIT"},"validators":["n3","n0","n1","n2","n4"]}
{"action":"change-state","created":1519105370.538523,"logger":"consensus","node":"n3","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n3","n0","n1","n2","n4"]}
{"action":"change-state","created":1519105370.574273,"logger":"consensus","node":"n3","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n3","n0","n1","n2","n4"]}
{"action":"save-message","created":1519105370.575648,"logger":"consensus","message":"e2928082160011e8bc6d0050b68fda61","node":"n3"}
["------------------------------------"]
{"action":"change-state","created":1519105361.3331351,"logger":"consensus","node":"n4","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105361.333357,"logger":"consensus","node":"n4","target":"n4","validators":["n4"]}
{"action":"connected","created":1519105363.4862988,"logger":"consensus","node":"n4","target":"n0","validators":["n4","n0"]}
{"action":"connected","created":1519105363.5541272,"logger":"consensus","node":"n4","target":"n1","validators":["n4","n0","n1"]}
{"action":"connected","created":1519105363.614958,"logger":"consensus","node":"n4","target":"n2","validators":["n4","n0","n1","n2"]}
{"action":"connected","created":1519105363.652483,"logger":"consensus","node":"n4","target":"n3","validators":["n4","n0","n1","n2","n3"]}
{"action":"connected","created":1519105363.6654289,"logger":"consensus","node":"n4","target":"n5","validators":["n4","n0","n1","n2","n3","n5"]}
{"action":"change-state","created":1519105365.669763,"logger":"consensus","node":"n4","state":{"after":"INIT","before":"INIT"},"validators":["n4","n0","n1","n2","n3","n5"]}
["------------------------------------"]
{"action":"change-state","created":1519105361.334327,"logger":"consensus","node":"n5","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105361.334579,"logger":"consensus","node":"n5","target":"n5","validators":["n5"]}
{"action":"connected","created":1519105363.450273,"logger":"consensus","node":"n5","target":"n4","validators":["n5","n4"]}
{"action":"connected","created":1519105363.507137,"logger":"consensus","node":"n5","target":"n6","validators":["n5","n4","n6"]}
{"action":"connected","created":1519105363.576226,"logger":"consensus","node":"n5","target":"n7","validators":["n5","n4","n6","n7"]}
{"action":"connected","created":1519105363.624573,"logger":"consensus","node":"n5","target":"n8","validators":["n5","n4","n6","n7","n8"]}
{"action":"change-state","created":1519105365.638562,"logger":"consensus","node":"n5","state":{"after":"INIT","before":"INIT"},"validators":["n5","n4","n6","n7","n8"]}
["------------------------------------"]
{"action":"change-state","created":1519105361.335458,"logger":"consensus","node":"n6","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105361.335666,"logger":"consensus","node":"n6","target":"n6","validators":["n6"]}
{"action":"connected","created":1519105363.4540071,"logger":"consensus","node":"n6","target":"n4","validators":["n6","n4"]}
{"action":"connected","created":1519105363.5190349,"logger":"consensus","node":"n6","target":"n5","validators":["n6","n4","n5"]}
{"action":"connected","created":1519105363.594557,"logger":"consensus","node":"n6","target":"n7","validators":["n6","n4","n5","n7"]}
{"action":"connected","created":1519105363.6357388,"logger":"consensus","node":"n6","target":"n8","validators":["n6","n4","n5","n7","n8"]}
{"action":"change-state","created":1519105365.649725,"logger":"consensus","node":"n6","state":{"after":"INIT","before":"INIT"},"validators":["n6","n4","n5","n7","n8"]}
["------------------------------------"]
{"action":"change-state","created":1519105361.3365939,"logger":"consensus","node":"n7","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105361.3367622,"logger":"consensus","node":"n7","target":"n7","validators":["n7"]}
{"action":"connected","created":1519105363.4734771,"logger":"consensus","node":"n7","target":"n4","validators":["n7","n4"]}
{"action":"connected","created":1519105363.569855,"logger":"consensus","node":"n7","target":"n5","validators":["n7","n4","n5"]}
{"action":"connected","created":1519105363.616622,"logger":"consensus","node":"n7","target":"n6","validators":["n7","n4","n5","n6"]}
{"action":"connected","created":1519105363.660081,"logger":"consensus","node":"n7","target":"n8","validators":["n7","n4","n5","n6","n8"]}
{"action":"change-state","created":1519105365.670209,"logger":"consensus","node":"n7","state":{"after":"INIT","before":"INIT"},"validators":["n7","n4","n5","n6","n8"]}
["------------------------------------"]
{"action":"change-state","created":1519105361.337706,"logger":"consensus","node":"n8","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105361.3378901,"logger":"consensus","node":"n8","target":"n8","validators":["n8"]}
{"action":"connected","created":1519105363.473061,"logger":"consensus","node":"n8","target":"n4","validators":["n8","n4"]}
{"action":"connected","created":1519105363.550208,"logger":"consensus","node":"n8","target":"n5","validators":["n8","n4","n5"]}
{"action":"connected","created":1519105363.628383,"logger":"consensus","node":"n8","target":"n6","validators":["n8","n4","n5","n6"]}
{"action":"connected","created":1519105363.659584,"logger":"consensus","node":"n8","target":"n7","validators":["n8","n4","n5","n6","n7"]}
{"action":"change-state","created":1519105365.663137,"logger":"consensus","node":"n8","state":{"after":"INIT","before":"INIT"},"validators":["n8","n4","n5","n6","n7"]}
```

* filtered the `save-message` actions
```json
{"action":"save-message","created":1519105370.562658,"logger":"consensus","message":"e2928082160011e8bc6d0050b68fda61","node":"n0"}
{"action":"save-message","created":1519105370.606077,"logger":"consensus","message":"e2928082160011e8bc6d0050b68fda61","node":"n1"}
{"action":"save-message","created":1519105370.599231,"logger":"consensus","message":"e2928082160011e8bc6d0050b68fda61","node":"n2"}
{"action":"save-message","created":1519105370.575648,"logger":"consensus","message":"e2928082160011e8bc6d0050b68fda61","node":"n3"}
```

`n4` is the common node between `q0` and `q1`, if it failed, the message was not broadcasted to the `q1`, so only `q0` was reached to the `ALLCONFIRM`.

## One Faulty Node In 2 Commons: `safe-common-2-1-is-faulty.yml`

* the important metric messages in all nodes
```json
["------------------------------------"]
{"action":"change-state","created":1519105822.585845,"logger":"consensus","node":"n0","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105822.58635,"logger":"consensus","node":"n0","target":"n0","validators":["n0"]}
{"action":"connected","created":1519105824.74597,"logger":"consensus","node":"n0","target":"n1","validators":["n0","n1"]}
{"action":"connected","created":1519105824.767555,"logger":"consensus","node":"n0","target":"n2","validators":["n0","n1","n2"]}
{"action":"connected","created":1519105824.818796,"logger":"consensus","node":"n0","target":"n3","validators":["n0","n1","n2","n3"]}
{"action":"connected","created":1519105824.870805,"logger":"consensus","node":"n0","target":"n4","validators":["n0","n1","n2","n3","n4"]}
{"action":"change-state","created":1519105826.884653,"logger":"consensus","node":"n0","state":{"after":"INIT","before":"INIT"},"validators":["n0","n1","n2","n3","n4"]}
{"action":"change-state","created":1519105829.782567,"logger":"consensus","node":"n0","state":{"after":"SIGN","before":"INIT"},"validators":["n0","n1","n2","n3","n4"]}
{"action":"change-state","created":1519105830.835625,"logger":"consensus","node":"n0","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n0","n1","n2","n3","n4"]}
{"action":"change-state","created":1519105830.857644,"logger":"consensus","node":"n0","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n0","n1","n2","n3","n4"]}
{"action":"save-message","created":1519105830.858902,"logger":"consensus","message":"f46b34f6160111e8af220050b68fda61","node":"n0"}
["------------------------------------"]
{"action":"change-state","created":1519105822.6400461,"logger":"consensus","node":"n1","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105822.640486,"logger":"consensus","node":"n1","target":"n1","validators":["n1"]}
{"action":"connected","created":1519105824.767283,"logger":"consensus","node":"n1","target":"n0","validators":["n1","n0"]}
{"action":"connected","created":1519105824.8116102,"logger":"consensus","node":"n1","target":"n2","validators":["n1","n0","n2"]}
{"action":"connected","created":1519105824.840044,"logger":"consensus","node":"n1","target":"n3","validators":["n1","n0","n2","n3"]}
{"action":"connected","created":1519105824.9037251,"logger":"consensus","node":"n1","target":"n4","validators":["n1","n0","n2","n3","n4"]}
{"action":"change-state","created":1519105826.913296,"logger":"consensus","node":"n1","state":{"after":"INIT","before":"INIT"},"validators":["n1","n0","n2","n3","n4"]}
{"action":"receive-message","created":1519105828.7093172,"logger":"blockchain","messge":"f46b34f6160111e8af220050b68fda61","node":"n1","state":"INIT"}
{"action":"change-state","created":1519105829.8325608,"logger":"consensus","node":"n1","state":{"after":"SIGN","before":"INIT"},"validators":["n1","n0","n2","n3","n4"]}
{"action":"change-state","created":1519105829.853446,"logger":"consensus","node":"n1","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n1","n0","n2","n3","n4"]}
{"action":"change-state","created":1519105830.876971,"logger":"consensus","node":"n1","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n1","n0","n2","n3","n4"]}
{"action":"save-message","created":1519105830.8772311,"logger":"consensus","message":"f46b34f6160111e8af220050b68fda61","node":"n1"}
["------------------------------------"]
{"action":"change-state","created":1519105822.642087,"logger":"consensus","node":"n2","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105822.642304,"logger":"consensus","node":"n2","target":"n2","validators":["n2"]}
{"action":"connected","created":1519105824.758133,"logger":"consensus","node":"n2","target":"n0","validators":["n2","n0"]}
{"action":"connected","created":1519105824.800225,"logger":"consensus","node":"n2","target":"n1","validators":["n2","n0","n1"]}
{"action":"connected","created":1519105824.8328588,"logger":"consensus","node":"n2","target":"n3","validators":["n2","n0","n1","n3"]}
{"action":"connected","created":1519105824.897413,"logger":"consensus","node":"n2","target":"n4","validators":["n2","n0","n1","n3","n4"]}
{"action":"change-state","created":1519105826.905584,"logger":"consensus","node":"n2","state":{"after":"INIT","before":"INIT"},"validators":["n2","n0","n1","n3","n4"]}
{"action":"change-state","created":1519105829.789402,"logger":"consensus","node":"n2","state":{"after":"SIGN","before":"INIT"},"validators":["n2","n0","n1","n3","n4"]}
{"action":"change-state","created":1519105830.820155,"logger":"consensus","node":"n2","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n2","n0","n1","n3","n4"]}
{"action":"change-state","created":1519105830.8346932,"logger":"consensus","node":"n2","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n2","n0","n1","n3","n4"]}
{"action":"save-message","created":1519105830.8349729,"logger":"consensus","message":"f46b34f6160111e8af220050b68fda61","node":"n2"}
["------------------------------------"]
{"action":"change-state","created":1519105822.643563,"logger":"consensus","node":"n3","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105822.643776,"logger":"consensus","node":"n3","target":"n3","validators":["n3"]}
{"action":"connected","created":1519105824.7441862,"logger":"consensus","node":"n3","target":"n0","validators":["n3","n0"]}
{"action":"connected","created":1519105824.7729301,"logger":"consensus","node":"n3","target":"n1","validators":["n3","n0","n1"]}
{"action":"connected","created":1519105824.828264,"logger":"consensus","node":"n3","target":"n2","validators":["n3","n0","n1","n2"]}
{"action":"connected","created":1519105824.874111,"logger":"consensus","node":"n3","target":"n4","validators":["n3","n0","n1","n2","n4"]}
{"action":"connected","created":1519105824.906892,"logger":"consensus","node":"n3","target":"n5","validators":["n3","n0","n1","n2","n4","n5"]}
{"action":"change-state","created":1519105826.924742,"logger":"consensus","node":"n3","state":{"after":"INIT","before":"INIT"},"validators":["n3","n0","n1","n2","n4","n5"]}
{"action":"change-state","created":1519105829.8416781,"logger":"consensus","node":"n3","state":{"after":"SIGN","before":"INIT"},"validators":["n3","n0","n1","n2","n4","n5"]}
{"action":"change-state","created":1519105829.865864,"logger":"consensus","node":"n3","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n3","n0","n1","n2","n4","n5"]}
{"action":"change-state","created":1519105830.885636,"logger":"consensus","node":"n3","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n3","n0","n1","n2","n4","n5"]}
{"action":"save-message","created":1519105830.8860319,"logger":"consensus","message":"f46b34f6160111e8af220050b68fda61","node":"n3"}
["------------------------------------"]
{"action":"change-state","created":1519105822.644821,"logger":"consensus","node":"n4","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105822.645026,"logger":"consensus","node":"n4","target":"n4","validators":["n4"]}
{"action":"connected","created":1519105824.756224,"logger":"consensus","node":"n4","target":"n0","validators":["n4","n0"]}
{"action":"connected","created":1519105824.799252,"logger":"consensus","node":"n4","target":"n1","validators":["n4","n0","n1"]}
{"action":"connected","created":1519105824.837152,"logger":"consensus","node":"n4","target":"n2","validators":["n4","n0","n1","n2"]}
{"action":"connected","created":1519105824.874482,"logger":"consensus","node":"n4","target":"n3","validators":["n4","n0","n1","n2","n3"]}
{"action":"connected","created":1519105824.9089348,"logger":"consensus","node":"n4","target":"n5","validators":["n4","n0","n1","n2","n3","n5"]}
{"action":"change-state","created":1519105826.9223082,"logger":"consensus","node":"n4","state":{"after":"INIT","before":"INIT"},"validators":["n4","n0","n1","n2","n3","n5"]}
["------------------------------------"]
{"action":"change-state","created":1519105822.646243,"logger":"consensus","node":"n5","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105822.64644,"logger":"consensus","node":"n5","target":"n5","validators":["n5"]}
{"action":"connected","created":1519105824.771359,"logger":"consensus","node":"n5","target":"n3","validators":["n5","n3"]}
{"action":"connected","created":1519105824.8416939,"logger":"consensus","node":"n5","target":"n4","validators":["n5","n3","n4"]}
{"action":"connected","created":1519105824.8928819,"logger":"consensus","node":"n5","target":"n6","validators":["n5","n3","n4","n6"]}
{"action":"connected","created":1519105824.916437,"logger":"consensus","node":"n5","target":"n7","validators":["n5","n3","n4","n6","n7"]}
{"action":"connected","created":1519105824.932876,"logger":"consensus","node":"n5","target":"n8","validators":["n5","n3","n4","n6","n7","n8"]}
{"action":"change-state","created":1519105826.936498,"logger":"consensus","node":"n5","state":{"after":"INIT","before":"INIT"},"validators":["n5","n3","n4","n6","n7","n8"]}
{"action":"change-state","created":1519105832.7824562,"logger":"consensus","node":"n5","state":{"after":"SIGN","before":"INIT"},"validators":["n5","n3","n4","n6","n7","n8"]}
{"action":"change-state","created":1519105832.795573,"logger":"consensus","node":"n5","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n5","n3","n4","n6","n7","n8"]}
{"action":"change-state","created":1519105833.814722,"logger":"consensus","node":"n5","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n5","n3","n4","n6","n7","n8"]}
{"action":"save-message","created":1519105833.8150988,"logger":"consensus","message":"f46b34f6160111e8af220050b68fda61","node":"n5"}
["------------------------------------"]
{"action":"change-state","created":1519105822.663742,"logger":"consensus","node":"n6","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105822.664093,"logger":"consensus","node":"n6","target":"n6","validators":["n6"]}
{"action":"connected","created":1519105824.763412,"logger":"consensus","node":"n6","target":"n3","validators":["n6","n3"]}
{"action":"connected","created":1519105824.8194602,"logger":"consensus","node":"n6","target":"n4","validators":["n6","n3","n4"]}
{"action":"connected","created":1519105824.852127,"logger":"consensus","node":"n6","target":"n5","validators":["n6","n3","n4","n5"]}
{"action":"connected","created":1519105824.8998,"logger":"consensus","node":"n6","target":"n7","validators":["n6","n3","n4","n5","n7"]}
{"action":"connected","created":1519105824.93363,"logger":"consensus","node":"n6","target":"n8","validators":["n6","n3","n4","n5","n7","n8"]}
{"action":"change-state","created":1519105826.936567,"logger":"consensus","node":"n6","state":{"after":"INIT","before":"INIT"},"validators":["n6","n3","n4","n5","n7","n8"]}
{"action":"change-state","created":1519105831.858346,"logger":"consensus","node":"n6","state":{"after":"SIGN","before":"INIT"},"validators":["n6","n3","n4","n5","n7","n8"]}
{"action":"change-state","created":1519105832.89378,"logger":"consensus","node":"n6","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n6","n3","n4","n5","n7","n8"]}
{"action":"change-state","created":1519105832.941427,"logger":"consensus","node":"n6","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n6","n3","n4","n5","n7","n8"]}
{"action":"save-message","created":1519105832.941683,"logger":"consensus","message":"f46b34f6160111e8af220050b68fda61","node":"n6"}
["------------------------------------"]
{"action":"change-state","created":1519105822.665317,"logger":"consensus","node":"n7","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105822.665566,"logger":"consensus","node":"n7","target":"n7","validators":["n7"]}
{"action":"connected","created":1519105824.75906,"logger":"consensus","node":"n7","target":"n3","validators":["n7","n3"]}
{"action":"connected","created":1519105824.807006,"logger":"consensus","node":"n7","target":"n4","validators":["n7","n3","n4"]}
{"action":"connected","created":1519105824.8338492,"logger":"consensus","node":"n7","target":"n5","validators":["n7","n3","n4","n5"]}
{"action":"connected","created":1519105824.8639271,"logger":"consensus","node":"n7","target":"n6","validators":["n7","n3","n4","n5","n6"]}
{"action":"connected","created":1519105824.898006,"logger":"consensus","node":"n7","target":"n8","validators":["n7","n3","n4","n5","n6","n8"]}
{"action":"change-state","created":1519105826.91017,"logger":"consensus","node":"n7","state":{"after":"INIT","before":"INIT"},"validators":["n7","n3","n4","n5","n6","n8"]}
{"action":"change-state","created":1519105831.8493419,"logger":"consensus","node":"n7","state":{"after":"SIGN","before":"INIT"},"validators":["n7","n3","n4","n5","n6","n8"]}
{"action":"change-state","created":1519105832.88161,"logger":"consensus","node":"n7","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n7","n3","n4","n5","n6","n8"]}
{"action":"change-state","created":1519105833.935346,"logger":"consensus","node":"n7","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n7","n3","n4","n5","n6","n8"]}
{"action":"save-message","created":1519105833.936151,"logger":"consensus","message":"f46b34f6160111e8af220050b68fda61","node":"n7"}
["------------------------------------"]
{"action":"change-state","created":1519105822.666937,"logger":"consensus","node":"n8","state":{"after":"INIT","before":null},"validators":[]}
{"action":"connected","created":1519105822.6672919,"logger":"consensus","node":"n8","target":"n8","validators":["n8"]}
{"action":"connected","created":1519105824.776478,"logger":"consensus","node":"n8","target":"n3","validators":["n8","n3"]}
{"action":"connected","created":1519105824.855793,"logger":"consensus","node":"n8","target":"n4","validators":["n8","n3","n4"]}
{"action":"connected","created":1519105824.893672,"logger":"consensus","node":"n8","target":"n5","validators":["n8","n3","n4","n5"]}
{"action":"connected","created":1519105824.918128,"logger":"consensus","node":"n8","target":"n6","validators":["n8","n3","n4","n5","n6"]}
{"action":"connected","created":1519105824.931905,"logger":"consensus","node":"n8","target":"n7","validators":["n8","n3","n4","n5","n6","n7"]}
{"action":"change-state","created":1519105826.9348962,"logger":"consensus","node":"n8","state":{"after":"INIT","before":"INIT"},"validators":["n8","n3","n4","n5","n6","n7"]}
{"action":"change-state","created":1519105831.853605,"logger":"consensus","node":"n8","state":{"after":"SIGN","before":"INIT"},"validators":["n8","n3","n4","n5","n6","n7"]}
{"action":"change-state","created":1519105832.8887959,"logger":"consensus","node":"n8","state":{"after":"ACCEPT","before":"SIGN"},"validators":["n8","n3","n4","n5","n6","n7"]}
{"action":"change-state","created":1519105833.9360461,"logger":"consensus","node":"n8","state":{"after":"ALLCONFIRM","before":"ACCEPT"},"validators":["n8","n3","n4","n5","n6","n7"]}
{"action":"save-message","created":1519105833.9364831,"logger":"consensus","message":"f46b34f6160111e8af220050b68fda61","node":"n8"}
```

* filtered the `save-message` actions
```json
{"action":"save-message","created":1519105830.8349729,"logger":"consensus","message":"f46b34f6160111e8af220050b68fda61","node":"n2"}
{"action":"save-message","created":1519105830.858902,"logger":"consensus","message":"f46b34f6160111e8af220050b68fda61","node":"n0"}
{"action":"save-message","created":1519105830.8772311,"logger":"consensus","message":"f46b34f6160111e8af220050b68fda61","node":"n1"}
{"action":"save-message","created":1519105830.8860319,"logger":"consensus","message":"f46b34f6160111e8af220050b68fda61","node":"n3"}
{"action":"save-message","created":1519105832.941683,"logger":"consensus","message":"f46b34f6160111e8af220050b68fda61","node":"n6"}
{"action":"save-message","created":1519105833.8150988,"logger":"consensus","message":"f46b34f6160111e8af220050b68fda61","node":"n5"}
{"action":"save-message","created":1519105833.936151,"logger":"consensus","message":"f46b34f6160111e8af220050b68fda61","node":"n7"}
{"action":"save-message","created":1519105833.9364831,"logger":"consensus","message":"f46b34f6160111e8af220050b68fda61","node":"n8"}
```

One faulty node in 2 common nodes, all the quorum was reached the consensus.
