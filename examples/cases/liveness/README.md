# Verifying Quroum Safety

For detailed process of this issues, please check [BOS-185](https://blockchainos.atlassian.net/browse/BOS-185).

## Running

The `run-case.py` will just launch the servers, which are instructed by design yaml file, so to occur the consensus, we need to run `run-client.py` to send message to server.

```sh
$ cd ./examples/cases
```

## Design: `liveness-1-is-faulty.yml`

```sh
$ python run-case.py -log-level info -log-output-metric /tmp/metric_liveness.json liveness/liveness-1-is-faulty.yml
```

Check that state of all nodes are changed to INIT
and then send message
```sh
$ python ../../scripts/run-client-new.py http://localhost:54320
```

Check that state of all nodes are changed to ALL_CONFIRM
and then send message again

```sh
$ python ../../scripts/run-client-new.py http://localhost:54320
```

> The `54320` is already assigned port by the design file for the node, 'n1'.

### Verifying In Logs

* the metric messages in all nodes - /tmp/metric_liveness.json

```json
["------------------------------------"]
{"action": "connected", "target": "n0", "validators": ["n0"], "logger": "consensus", "node": "n0", "created": 1519348561.513113}
{"action": "change-state", "node": "n0", "state": {"after": "INIT", "before": null}, "validators": ["n0"], "logger": "consensus", "created": 1519348561.513524}
{"action": "connected", "target": "n1", "validators": ["n1"], "logger": "consensus", "node": "n1", "created": 1519348561.658516}
{"action": "change-state", "node": "n1", "state": {"after": "INIT", "before": null}, "validators": ["n1"], "logger": "consensus", "created": 1519348561.658944}
{"action": "connected", "target": "n2", "validators": ["n2"], "logger": "consensus", "node": "n2", "created": 1519348561.6599932}
{"action": "change-state", "node": "n2", "state": {"after": "INIT", "before": null}, "validators": ["n2"], "logger": "consensus", "created": 1519348561.660199}
{"action": "connected", "target": "n3", "validators": ["n3"], "logger": "consensus", "node": "n3", "created": 1519348561.66125}
{"action": "change-state", "node": "n3", "state": {"after": "INIT", "before": null}, "validators": ["n3"], "logger": "consensus", "created": 1519348561.661453}
{"action": "connected", "target": "n4", "validators": ["n4"], "logger": "consensus", "node": "n4", "created": 1519348561.662663}
{"action": "change-state", "node": "n4", "state": {"after": "INIT", "before": null}, "validators": ["n4"], "logger": "consensus", "created": 1519348561.663121}
{"action": "connected", "target": "n5", "validators": ["n5"], "logger": "consensus", "node": "n5", "created": 1519348561.6653051}
{"action": "change-state", "node": "n5", "state": {"after": "INIT", "before": null}, "validators": ["n5"], "logger": "consensus", "created": 1519348561.665793}
{"action": "connected", "target": "n6", "validators": ["n6"], "logger": "consensus", "node": "n6", "created": 1519348561.66682}
{"action": "change-state", "node": "n6", "state": {"after": "INIT", "before": null}, "validators": ["n6"], "logger": "consensus", "created": 1519348561.667027}
{"action": "connected", "target": "n7", "validators": ["n7"], "logger": "consensus", "node": "n7", "created": 1519348561.6679838}
{"action": "change-state", "node": "n7", "state": {"after": "INIT", "before": null}, "validators": ["n7"], "logger": "consensus", "created": 1519348561.6682172}
{"action": "connected", "target": "n0", "validators": ["n2", "n0"], "logger": "consensus", "node": "n2", "created": 1519348563.728537}
{"action": "connected", "target": "n1", "validators": ["n4", "n1"], "logger": "consensus", "node": "n4", "created": 1519348563.73558}
{"action": "connected", "target": "n1", "validators": ["n5", "n1"], "logger": "consensus", "node": "n5", "created": 1519348563.737956}
{"action": "connected", "target": "n0", "validators": ["n1", "n0"], "logger": "consensus", "node": "n1", "created": 1519348563.738726}
{"action": "connected", "target": "n1", "validators": ["n0", "n1"], "logger": "consensus", "node": "n0", "created": 1519348563.74639}
{"action": "connected", "target": "n0", "validators": ["n6", "n0"], "logger": "consensus", "node": "n6", "created": 1519348563.747612}
{"action": "connected", "target": "n0", "validators": ["n3", "n0"], "logger": "consensus", "node": "n3", "created": 1519348563.748328}
{"action": "connected", "target": "n1", "validators": ["n7", "n1"], "logger": "consensus", "node": "n7", "created": 1519348563.7578702}
{"action": "connected", "target": "n1", "validators": ["n2", "n0", "n1"], "logger": "consensus", "node": "n2", "created": 1519348563.7684412}
{"action": "connected", "target": "n2", "validators": ["n1", "n0", "n2"], "logger": "consensus", "node": "n1", "created": 1519348563.770742}
{"action": "connected", "target": "n2", "validators": ["n4", "n1", "n2"], "logger": "consensus", "node": "n4", "created": 1519348563.7837021}
{"action": "connected", "target": "n2", "validators": ["n5", "n1", "n2"], "logger": "consensus", "node": "n5", "created": 1519348563.801843}
{"action": "connected", "target": "n2", "validators": ["n0", "n1", "n2"], "logger": "consensus", "node": "n0", "created": 1519348563.802588}
{"action": "connected", "target": "n1", "validators": ["n3", "n0", "n1"], "logger": "consensus", "node": "n3", "created": 1519348563.8031301}
{"action": "connected", "target": "n1", "validators": ["n6", "n0", "n1"], "logger": "consensus", "node": "n6", "created": 1519348563.805712}
{"action": "connected", "target": "n2", "validators": ["n7", "n1", "n2"], "logger": "consensus", "node": "n7", "created": 1519348563.807085}
{"action": "connected", "target": "n3", "validators": ["n2", "n0", "n1", "n3"], "logger": "consensus", "node": "n2", "created": 1519348563.820276}
{"action": "connected", "target": "n3", "validators": ["n1", "n0", "n2", "n3"], "logger": "consensus", "node": "n1", "created": 1519348563.829005}
{"action": "connected", "target": "n3", "validators": ["n4", "n1", "n2", "n3"], "logger": "consensus", "node": "n4", "created": 1519348563.8328059}
{"action": "connected", "target": "n3", "validators": ["n5", "n1", "n2", "n3"], "logger": "consensus", "node": "n5", "created": 1519348563.84579}
{"action": "connected", "target": "n2", "validators": ["n3", "n0", "n1", "n2"], "logger": "consensus", "node": "n3", "created": 1519348563.85855}
{"action": "connected", "target": "n3", "validators": ["n0", "n1", "n2", "n3"], "logger": "consensus", "node": "n0", "created": 1519348563.8600278}
{"action": "connected", "target": "n2", "validators": ["n6", "n0", "n1", "n2"], "logger": "consensus", "node": "n6", "created": 1519348563.869719}
{"action": "connected", "target": "n4", "validators": ["n2", "n0", "n1", "n3", "n4"], "logger": "consensus", "node": "n2", "created": 1519348563.885914}
{"action": "connected", "target": "n3", "validators": ["n7", "n1", "n2", "n3"], "logger": "consensus", "node": "n7", "created": 1519348563.8888671}
{"action": "connected", "target": "n5", "validators": ["n4", "n1", "n2", "n3", "n5"], "logger": "consensus", "node": "n4", "created": 1519348563.891667}
{"action": "connected", "target": "n4", "validators": ["n1", "n0", "n2", "n3", "n4"], "logger": "consensus", "node": "n1", "created": 1519348563.913023}
{"action": "connected", "target": "n3", "validators": ["n6", "n0", "n1", "n2", "n3"], "logger": "consensus", "node": "n6", "created": 1519348563.913693}
{"action": "connected", "target": "n4", "validators": ["n5", "n1", "n2", "n3", "n4"], "logger": "consensus", "node": "n5", "created": 1519348563.9147751}
{"action": "connected", "target": "n4", "validators": ["n3", "n0", "n1", "n2", "n4"], "logger": "consensus", "node": "n3", "created": 1519348563.936523}
{"action": "connected", "target": "n5", "validators": ["n2", "n0", "n1", "n3", "n4", "n5"], "logger": "consensus", "node": "n2", "created": 1519348563.94064}
{"action": "connected", "target": "n4", "validators": ["n0", "n1", "n2", "n3", "n4"], "logger": "consensus", "node": "n0", "created": 1519348563.941474}
{"action": "connected", "target": "n6", "validators": ["n4", "n1", "n2", "n3", "n5", "n6"], "logger": "consensus", "node": "n4", "created": 1519348563.949749}
{"action": "connected", "target": "n4", "validators": ["n7", "n1", "n2", "n3", "n4"], "logger": "consensus", "node": "n7", "created": 1519348563.954721}
{"action": "connected", "target": "n4", "validators": ["n6", "n0", "n1", "n2", "n3", "n4"], "logger": "consensus", "node": "n6", "created": 1519348563.959378}
{"action": "connected", "target": "n5", "validators": ["n1", "n0", "n2", "n3", "n4", "n5"], "logger": "consensus", "node": "n1", "created": 1519348563.968991}
{"action": "connected", "target": "n6", "validators": ["n5", "n1", "n2", "n3", "n4", "n6"], "logger": "consensus", "node": "n5", "created": 1519348563.979925}
{"action": "connected", "target": "n5", "validators": ["n3", "n0", "n1", "n2", "n4", "n5"], "logger": "consensus", "node": "n3", "created": 1519348563.993097}
{"action": "connected", "target": "n6", "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "node": "n2", "created": 1519348563.99419}
{"action": "connected", "target": "n5", "validators": ["n0", "n1", "n2", "n3", "n4", "n5"], "logger": "consensus", "node": "n0", "created": 1519348564.006558}
{"action": "connected", "target": "n7", "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "node": "n4", "created": 1519348564.007016}
{"action": "connected", "target": "n7", "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "node": "n5", "created": 1519348564.021441}
{"action": "connected", "target": "n5", "validators": ["n6", "n0", "n1", "n2", "n3", "n4", "n5"], "logger": "consensus", "node": "n6", "created": 1519348564.0221062}
{"action": "connected", "target": "n6", "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "node": "n1", "created": 1519348564.030221}
{"action": "connected", "target": "n6", "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "node": "n3", "created": 1519348564.032096}
{"action": "connected", "target": "n5", "validators": ["n7", "n1", "n2", "n3", "n4", "n5"], "logger": "consensus", "node": "n7", "created": 1519348564.034834}
{"action": "connected", "target": "n7", "validators": ["n6", "n0", "n1", "n2", "n3", "n4", "n5", "n7"], "logger": "consensus", "node": "n6", "created": 1519348564.0443761}
{"action": "connected", "target": "n6", "validators": ["n0", "n1", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "node": "n0", "created": 1519348564.048543}
{"action": "connected", "target": "n6", "validators": ["n7", "n1", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "node": "n7", "created": 1519348564.051164}
{"action": "change-state", "node": "n2", "state": {"after": "INIT", "before": "INIT"}, "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348565.996408}
{"action": "change-state", "node": "n4", "state": {"after": "INIT", "before": "INIT"}, "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "created": 1519348566.012705}
{"action": "change-state", "node": "n5", "state": {"after": "INIT", "before": "INIT"}, "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "created": 1519348566.026069}
{"action": "change-state", "node": "n1", "state": {"after": "INIT", "before": "INIT"}, "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348566.031413}
{"action": "change-state", "node": "n3", "state": {"after": "INIT", "before": "INIT"}, "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348566.036182}
{"action": "change-state", "node": "n6", "state": {"after": "INIT", "before": "INIT"}, "validators": ["n6", "n0", "n1", "n2", "n3", "n4", "n5", "n7"], "logger": "consensus", "created": 1519348566.0485718}
{"action": "change-state", "node": "n0", "state": {"after": "INIT", "before": "INIT"}, "validators": ["n0", "n1", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348566.0498738}
{"action": "change-state", "node": "n7", "state": {"after": "INIT", "before": "INIT"}, "validators": ["n7", "n1", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348566.056373}
{"action": "receive-message", "messge": "221c8d5a183711e8826dda0004d06c00", "state": "INIT", "logger": "blockchain", "node": "n1", "created": 1519348571.706814}
{"action": "change-state", "node": "n4", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "created": 1519348573.3229928}
{"action": "change-state", "node": "n0", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n0", "n1", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348573.3345768}
{"action": "change-state", "node": "n3", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348573.3921542}
{"action": "change-state", "node": "n5", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "created": 1519348573.418237}
{"action": "change-state", "node": "n2", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348573.422123}
{"action": "change-state", "node": "n1", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348573.482296}
{"action": "change-state", "node": "n6", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n6", "n0", "n1", "n2", "n3", "n4", "n5", "n7"], "logger": "consensus", "created": 1519348573.4938939}
{"action": "change-state", "node": "n3", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348573.543742}
{"action": "change-state", "node": "n2", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348573.598185}
{"action": "change-state", "node": "n1", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348573.631624}
{"action": "change-state", "node": "n6", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n6", "n0", "n1", "n2", "n3", "n4", "n5", "n7"], "logger": "consensus", "created": 1519348573.638605}
{"action": "change-state", "node": "n4", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "created": 1519348574.502017}
{"action": "change-state", "node": "n0", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n0", "n1", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348574.506222}
{"action": "change-state", "node": "n0", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n0", "n1", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348574.55314}
{"message": "221c8d5a183711e8826dda0004d06c00", "action": "save-message", "logger": "consensus", "node": "n0", "created": 1519348574.553787}
{"action": "change-state", "node": "n4", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "created": 1519348574.554691}
{"message": "221c8d5a183711e8826dda0004d06c00", "action": "save-message", "logger": "consensus", "node": "n4", "created": 1519348574.5557609}
{"action": "change-state", "node": "n5", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "created": 1519348574.567613}
{"action": "change-state", "node": "n5", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "created": 1519348574.637504}
{"message": "221c8d5a183711e8826dda0004d06c00", "action": "save-message", "logger": "consensus", "node": "n5", "created": 1519348574.638098}
{"action": "change-state", "node": "n3", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348574.6804638}
{"message": "221c8d5a183711e8826dda0004d06c00", "action": "save-message", "logger": "consensus", "node": "n3", "created": 1519348574.680851}
{"action": "change-state", "node": "n2", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348574.708234}
{"message": "221c8d5a183711e8826dda0004d06c00", "action": "save-message", "logger": "consensus", "node": "n2", "created": 1519348574.708917}
{"action": "change-state", "node": "n1", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348574.7295492}
{"message": "221c8d5a183711e8826dda0004d06c00", "action": "save-message", "logger": "consensus", "node": "n1", "created": 1519348574.730261}
{"action": "change-state", "node": "n6", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n6", "n0", "n1", "n2", "n3", "n4", "n5", "n7"], "logger": "consensus", "created": 1519348574.738466}
{"message": "221c8d5a183711e8826dda0004d06c00", "action": "save-message", "logger": "consensus", "node": "n6", "created": 1519348574.74294}
{"checkpoint": 0, "validators": ["n3", "n1", "n5", "n6", "n4", "n2"], "voted_nodes": ["n2", "n3", "n1", "n6"], "no_voting_nodes": ["n4", "n5"], "logger": "audit.faulty-node.no-voting", "node": "n0", "created": 1519348579.189656}
{"checkpoint": 0, "validators": ["n3", "n5", "n0", "n6", "n4", "n2"], "voted_nodes": ["n3", "n5", "n0", "n6", "n4", "n2"], "no_voting_nodes": [], "logger": "audit.faulty-node.no-voting", "node": "n1", "created": 1519348579.1904042}
{"checkpoint": 0, "validators": ["n3", "n1", "n5", "n0", "n6", "n4"], "voted_nodes": ["n3", "n1", "n5", "n0", "n6", "n4"], "no_voting_nodes": [], "logger": "audit.faulty-node.no-voting", "node": "n2", "created": 1519348579.19088}
{"checkpoint": 0, "validators": ["n1", "n5", "n0", "n6", "n4", "n2"], "voted_nodes": ["n1", "n5", "n0", "n6", "n4", "n2"], "no_voting_nodes": [], "logger": "audit.faulty-node.no-voting", "node": "n3", "created": 1519348579.191305}
{"checkpoint": 0, "validators": ["n3", "n1", "n5", "n7", "n6", "n2"], "voted_nodes": ["n3", "n1", "n5", "n6", "n2"], "no_voting_nodes": ["n7"], "logger": "audit.faulty-node.no-voting", "node": "n4", "created": 1519348579.191723}
{"checkpoint": 0, "validators": ["n3", "n1", "n7", "n6", "n4", "n2"], "voted_nodes": ["n3", "n1", "n6", "n4", "n2"], "no_voting_nodes": ["n7"], "logger": "audit.faulty-node.no-voting", "node": "n5", "created": 1519348579.19214}
{"checkpoint": 0, "validators": ["n3", "n1", "n0", "n5", "n7", "n4", "n2"], "voted_nodes": ["n3", "n1", "n5", "n0", "n4", "n2"], "no_voting_nodes": ["n7"], "logger": "audit.faulty-node.no-voting", "node": "n6", "created": 1519348579.192498}
{"action": "receive-message", "messge": "2d4727f8183711e8a1b7da0004d06c00", "state": "ALLCONFIRM", "logger": "blockchain", "node": "n1", "created": 1519348589.8889952}
{"action": "change-state", "node": "n1", "state": {"after": "INIT", "before": "ALLCONFIRM"}, "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348589.889856}
{"action": "change-state", "node": "n0", "state": {"after": "INIT", "before": "ALLCONFIRM"}, "validators": ["n0", "n1", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348590.686573}
{"action": "change-state", "node": "n4", "state": {"after": "INIT", "before": "ALLCONFIRM"}, "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "created": 1519348590.697218}
{"action": "change-state", "node": "n5", "state": {"after": "INIT", "before": "ALLCONFIRM"}, "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "created": 1519348590.832924}
{"action": "change-state", "node": "n3", "state": {"after": "INIT", "before": "ALLCONFIRM"}, "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348590.8428218}
{"action": "change-state", "node": "n2", "state": {"after": "INIT", "before": "ALLCONFIRM"}, "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348590.8908858}
{"action": "change-state", "node": "n6", "state": {"after": "INIT", "before": "ALLCONFIRM"}, "validators": ["n6", "n0", "n1", "n2", "n3", "n4", "n5", "n7"], "logger": "consensus", "created": 1519348590.906838}
{"action": "change-state", "node": "n5", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "created": 1519348591.136457}
{"action": "change-state", "node": "n3", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348591.160767}
{"action": "change-state", "node": "n2", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348591.235902}
{"action": "change-state", "node": "n1", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348591.281213}
{"action": "change-state", "node": "n6", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n6", "n0", "n1", "n2", "n3", "n4", "n5", "n7"], "logger": "consensus", "created": 1519348591.332221}
{"action": "change-state", "node": "n6", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n6", "n0", "n1", "n2", "n3", "n4", "n5", "n7"], "logger": "consensus", "created": 1519348591.36933}
{"action": "change-state", "node": "n0", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n0", "n1", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348591.8541892}
{"action": "change-state", "node": "n4", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "created": 1519348591.8580108}
{"action": "change-state", "node": "n4", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "created": 1519348591.898547}
{"action": "change-state", "node": "n0", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n0", "n1", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348591.900355}
{"action": "change-state", "node": "n5", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "created": 1519348592.24872}
{"action": "change-state", "node": "n3", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348592.274132}
{"action": "change-state", "node": "n3", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348592.303058}
{"message": "2d4727f8183711e8a1b7da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n3", "created": 1519348592.303305}
{"action": "change-state", "node": "n2", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348592.32131}
{"action": "change-state", "node": "n1", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348592.3422499}
{"action": "change-state", "node": "n2", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348592.370019}
{"message": "2d4727f8183711e8a1b7da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n2", "created": 1519348592.37084}
{"action": "change-state", "node": "n1", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348592.395809}
{"message": "2d4727f8183711e8a1b7da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n1", "created": 1519348592.398763}
{"action": "change-state", "node": "n6", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n6", "n0", "n1", "n2", "n3", "n4", "n5", "n7"], "logger": "consensus", "created": 1519348592.4114282}
{"message": "2d4727f8183711e8a1b7da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n6", "created": 1519348592.411677}
{"action": "change-state", "node": "n4", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "created": 1519348592.942482}
{"message": "2d4727f8183711e8a1b7da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n4", "created": 1519348592.942898}
{"action": "change-state", "node": "n0", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n0", "n1", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348592.947999}
{"message": "2d4727f8183711e8a1b7da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n0", "created": 1519348592.949322}
{"action": "change-state", "node": "n5", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "created": 1519348593.285633}
{"message": "2d4727f8183711e8a1b7da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n5", "created": 1519348593.286052}
{"checkpoint": 19, "validators": ["n3", "n1", "n5", "n6", "n4", "n2"], "voted_nodes": ["n2", "n3", "n1", "n6"], "no_voting_nodes": ["n4", "n5"], "logger": "audit.faulty-node.no-voting", "node": "n0", "created": 1519348597.075378}
{"checkpoint": 31, "validators": ["n3", "n5", "n0", "n6", "n4", "n2"], "voted_nodes": ["n3", "n5", "n0", "n6", "n4", "n2"], "no_voting_nodes": [], "logger": "audit.faulty-node.no-voting", "node": "n1", "created": 1519348597.076113}
{"checkpoint": 29, "validators": ["n3", "n1", "n5", "n0", "n6", "n4"], "voted_nodes": ["n3", "n1", "n5", "n0", "n6", "n4"], "no_voting_nodes": [], "logger": "audit.faulty-node.no-voting", "node": "n2", "created": 1519348597.076566}
{"checkpoint": 29, "validators": ["n1", "n5", "n0", "n6", "n4", "n2"], "voted_nodes": ["n1", "n5", "n0", "n6", "n4", "n2"], "no_voting_nodes": [], "logger": "audit.faulty-node.no-voting", "node": "n3", "created": 1519348597.076977}
{"checkpoint": 24, "validators": ["n3", "n1", "n5", "n7", "n6", "n2"], "voted_nodes": ["n3", "n1", "n5", "n6", "n2"], "no_voting_nodes": ["n7"], "logger": "audit.faulty-node.no-voting", "node": "n4", "created": 1519348597.0773818}
{"checkpoint": 29, "validators": ["n3", "n1", "n0", "n5", "n7", "n4", "n2"], "voted_nodes": ["n3", "n1", "n5", "n0", "n4", "n2"], "no_voting_nodes": ["n7"], "logger": "audit.faulty-node.no-voting", "node": "n6", "created": 1519348597.0778399}
{"checkpoint": 24, "validators": ["n3", "n1", "n7", "n6", "n4", "n2"], "voted_nodes": ["n3", "n1", "n6", "n4", "n2"], "no_voting_nodes": ["n7"], "logger": "audit.faulty-node.no-voting", "node": "n5", "created": 1519348598.090135}
["------------------------------------"]
```

* Filtered by `liveness`
```sh
$ cat /tmp/metric_liveness.json | jq -S --indent 0 -r 'select(.liveness)' 2> /dev/null
```

> To run this bash script, we need `jq`. To install `jq`, `brew install jq`.

```json

```

This will show "n1" is liveness safe.


## Design: `liveness-fail-2-is-faulty.yml`

```sh
$ python run-case.py -log-level info -log-output-metric /tmp/metric_liveness.json liveness/liveness-fail-2-is-faulty.yml
```

Check that state of all nodes are changed to INIT
and then send message
```sh
$ python ../../scripts/run-client-new.py http://localhost:54320
```

Check that state of all nodes are changed to ALL_CONFIRM
and then send message again

```sh
$ python ../../scripts/run-client-new.py http://localhost:54320
```

> The `54320` is already assigned port by the design file for the node, 'n1'.

### Verifying In Logs

* the metric messages in all nodes - /tmp/metric_liveness.json

```json
["------------------------------------"]
{"action": "connected", "target": "n0", "validators": ["n0"], "logger": "consensus", "node": "n0", "created": 1519348325.19739}
{"action": "change-state", "node": "n0", "state": {"after": "INIT", "before": null}, "validators": ["n0"], "logger": "consensus", "created": 1519348325.1978822}
{"action": "connected", "target": "n1", "validators": ["n1"], "logger": "consensus", "node": "n1", "created": 1519348325.336982}
{"action": "change-state", "node": "n1", "state": {"after": "INIT", "before": null}, "validators": ["n1"], "logger": "consensus", "created": 1519348325.337441}
{"action": "connected", "target": "n2", "validators": ["n2"], "logger": "consensus", "node": "n2", "created": 1519348325.338732}
{"action": "change-state", "node": "n2", "state": {"after": "INIT", "before": null}, "validators": ["n2"], "logger": "consensus", "created": 1519348325.3390038}
{"action": "connected", "target": "n3", "validators": ["n3"], "logger": "consensus", "node": "n3", "created": 1519348325.340137}
{"action": "change-state", "node": "n3", "state": {"after": "INIT", "before": null}, "validators": ["n3"], "logger": "consensus", "created": 1519348325.3403862}
{"action": "connected", "target": "n4", "validators": ["n4"], "logger": "consensus", "node": "n4", "created": 1519348325.341527}
{"action": "change-state", "node": "n4", "state": {"after": "INIT", "before": null}, "validators": ["n4"], "logger": "consensus", "created": 1519348325.341825}
{"action": "connected", "target": "n5", "validators": ["n5"], "logger": "consensus", "node": "n5", "created": 1519348325.3427908}
{"action": "change-state", "node": "n5", "state": {"after": "INIT", "before": null}, "validators": ["n5"], "logger": "consensus", "created": 1519348325.3429692}
{"action": "connected", "target": "n6", "validators": ["n6"], "logger": "consensus", "node": "n6", "created": 1519348325.343893}
{"action": "change-state", "node": "n6", "state": {"after": "INIT", "before": null}, "validators": ["n6"], "logger": "consensus", "created": 1519348325.344084}
{"action": "connected", "target": "n7", "validators": ["n7"], "logger": "consensus", "node": "n7", "created": 1519348325.345053}
{"action": "change-state", "node": "n7", "state": {"after": "INIT", "before": null}, "validators": ["n7"], "logger": "consensus", "created": 1519348325.345226}
{"action": "connected", "target": "n1", "validators": ["n4", "n1"], "logger": "consensus", "node": "n4", "created": 1519348327.547242}
{"action": "connected", "target": "n1", "validators": ["n7", "n1"], "logger": "consensus", "node": "n7", "created": 1519348327.5535119}
{"action": "connected", "target": "n1", "validators": ["n0", "n1"], "logger": "consensus", "node": "n0", "created": 1519348327.565249}
{"action": "connected", "target": "n2", "validators": ["n4", "n1", "n2"], "logger": "consensus", "node": "n4", "created": 1519348327.5722098}
{"action": "connected", "target": "n0", "validators": ["n1", "n0"], "logger": "consensus", "node": "n1", "created": 1519348327.5727801}
{"action": "connected", "target": "n0", "validators": ["n2", "n0"], "logger": "consensus", "node": "n2", "created": 1519348327.574891}
{"action": "connected", "target": "n0", "validators": ["n3", "n0"], "logger": "consensus", "node": "n3", "created": 1519348327.57713}
{"action": "connected", "target": "n0", "validators": ["n6", "n0"], "logger": "consensus", "node": "n6", "created": 1519348327.585432}
{"action": "connected", "target": "n1", "validators": ["n5", "n1"], "logger": "consensus", "node": "n5", "created": 1519348327.609198}
{"action": "connected", "target": "n3", "validators": ["n4", "n1", "n2", "n3"], "logger": "consensus", "node": "n4", "created": 1519348327.632718}
{"action": "connected", "target": "n1", "validators": ["n2", "n0", "n1"], "logger": "consensus", "node": "n2", "created": 1519348327.634403}
{"action": "connected", "target": "n2", "validators": ["n7", "n1", "n2"], "logger": "consensus", "node": "n7", "created": 1519348327.637363}
{"action": "connected", "target": "n2", "validators": ["n1", "n0", "n2"], "logger": "consensus", "node": "n1", "created": 1519348327.639925}
{"action": "connected", "target": "n1", "validators": ["n6", "n0", "n1"], "logger": "consensus", "node": "n6", "created": 1519348327.6416268}
{"action": "connected", "target": "n1", "validators": ["n3", "n0", "n1"], "logger": "consensus", "node": "n3", "created": 1519348327.646219}
{"action": "connected", "target": "n2", "validators": ["n5", "n1", "n2"], "logger": "consensus", "node": "n5", "created": 1519348327.661772}
{"action": "connected", "target": "n2", "validators": ["n0", "n1", "n2"], "logger": "consensus", "node": "n0", "created": 1519348327.6644092}
{"action": "connected", "target": "n5", "validators": ["n4", "n1", "n2", "n3", "n5"], "logger": "consensus", "node": "n4", "created": 1519348327.676655}
{"action": "connected", "target": "n3", "validators": ["n2", "n0", "n1", "n3"], "logger": "consensus", "node": "n2", "created": 1519348327.687226}
{"action": "connected", "target": "n3", "validators": ["n7", "n1", "n2", "n3"], "logger": "consensus", "node": "n7", "created": 1519348327.6980228}
{"action": "connected", "target": "n2", "validators": ["n6", "n0", "n1", "n2"], "logger": "consensus", "node": "n6", "created": 1519348327.7014039}
{"action": "connected", "target": "n2", "validators": ["n3", "n0", "n1", "n2"], "logger": "consensus", "node": "n3", "created": 1519348327.707201}
{"action": "connected", "target": "n3", "validators": ["n1", "n0", "n2", "n3"], "logger": "consensus", "node": "n1", "created": 1519348327.708108}
{"action": "connected", "target": "n3", "validators": ["n0", "n1", "n2", "n3"], "logger": "consensus", "node": "n0", "created": 1519348327.719266}
{"action": "connected", "target": "n3", "validators": ["n5", "n1", "n2", "n3"], "logger": "consensus", "node": "n5", "created": 1519348327.72096}
{"action": "connected", "target": "n4", "validators": ["n2", "n0", "n1", "n3", "n4"], "logger": "consensus", "node": "n2", "created": 1519348327.724598}
{"action": "connected", "target": "n6", "validators": ["n4", "n1", "n2", "n3", "n5", "n6"], "logger": "consensus", "node": "n4", "created": 1519348327.725803}
{"action": "connected", "target": "n3", "validators": ["n6", "n0", "n1", "n2", "n3"], "logger": "consensus", "node": "n6", "created": 1519348327.748619}
{"action": "connected", "target": "n4", "validators": ["n7", "n1", "n2", "n3", "n4"], "logger": "consensus", "node": "n7", "created": 1519348327.750883}
{"action": "connected", "target": "n4", "validators": ["n1", "n0", "n2", "n3", "n4"], "logger": "consensus", "node": "n1", "created": 1519348327.7628381}
{"action": "connected", "target": "n4", "validators": ["n3", "n0", "n1", "n2", "n4"], "logger": "consensus", "node": "n3", "created": 1519348327.764352}
{"action": "connected", "target": "n5", "validators": ["n2", "n0", "n1", "n3", "n4", "n5"], "logger": "consensus", "node": "n2", "created": 1519348327.774858}
{"action": "connected", "target": "n7", "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "node": "n4", "created": 1519348327.779252}
{"action": "connected", "target": "n4", "validators": ["n0", "n1", "n2", "n3", "n4"], "logger": "consensus", "node": "n0", "created": 1519348327.779634}
{"action": "connected", "target": "n4", "validators": ["n5", "n1", "n2", "n3", "n4"], "logger": "consensus", "node": "n5", "created": 1519348327.78661}
{"action": "connected", "target": "n4", "validators": ["n6", "n0", "n1", "n2", "n3", "n4"], "logger": "consensus", "node": "n6", "created": 1519348327.788019}
{"action": "connected", "target": "n5", "validators": ["n7", "n1", "n2", "n3", "n4", "n5"], "logger": "consensus", "node": "n7", "created": 1519348327.8052459}
{"action": "connected", "target": "n5", "validators": ["n1", "n0", "n2", "n3", "n4", "n5"], "logger": "consensus", "node": "n1", "created": 1519348327.812614}
{"action": "connected", "target": "n6", "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "node": "n2", "created": 1519348327.816284}
{"action": "connected", "target": "n5", "validators": ["n3", "n0", "n1", "n2", "n4", "n5"], "logger": "consensus", "node": "n3", "created": 1519348327.818947}
{"action": "connected", "target": "n6", "validators": ["n5", "n1", "n2", "n3", "n4", "n6"], "logger": "consensus", "node": "n5", "created": 1519348327.8236742}
{"action": "connected", "target": "n5", "validators": ["n0", "n1", "n2", "n3", "n4", "n5"], "logger": "consensus", "node": "n0", "created": 1519348327.835045}
{"action": "connected", "target": "n6", "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "node": "n1", "created": 1519348327.8460422}
{"action": "connected", "target": "n6", "validators": ["n7", "n1", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "node": "n7", "created": 1519348327.847497}
{"action": "connected", "target": "n7", "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "node": "n5", "created": 1519348327.8490171}
{"action": "connected", "target": "n5", "validators": ["n6", "n0", "n1", "n2", "n3", "n4", "n5"], "logger": "consensus", "node": "n6", "created": 1519348327.8498309}
{"action": "connected", "target": "n6", "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "node": "n3", "created": 1519348327.851125}
{"action": "connected", "target": "n6", "validators": ["n0", "n1", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "node": "n0", "created": 1519348327.856653}
{"action": "connected", "target": "n7", "validators": ["n6", "n0", "n1", "n2", "n3", "n4", "n5", "n7"], "logger": "consensus", "node": "n6", "created": 1519348327.860538}
{"action": "change-state", "node": "n4", "state": {"after": "INIT", "before": "INIT"}, "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "created": 1519348329.782763}
{"action": "change-state", "node": "n2", "state": {"after": "INIT", "before": "INIT"}, "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348329.822347}
{"action": "change-state", "node": "n1", "state": {"after": "INIT", "before": "INIT"}, "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348329.846466}
{"action": "change-state", "node": "n5", "state": {"after": "INIT", "before": "INIT"}, "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "created": 1519348329.85285}
{"action": "change-state", "node": "n7", "state": {"after": "INIT", "before": "INIT"}, "validators": ["n7", "n1", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348329.853392}
{"action": "change-state", "node": "n3", "state": {"after": "INIT", "before": "INIT"}, "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348329.854323}
{"action": "change-state", "node": "n0", "state": {"after": "INIT", "before": "INIT"}, "validators": ["n0", "n1", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348329.859434}
{"action": "change-state", "node": "n6", "state": {"after": "INIT", "before": "INIT"}, "validators": ["n6", "n0", "n1", "n2", "n3", "n4", "n5", "n7"], "logger": "consensus", "created": 1519348329.8648582}
{"action": "receive-message", "messge": "94655f46183611e88198da0004d06c00", "state": "INIT", "logger": "blockchain", "node": "n1", "created": 1519348333.511681}
{"action": "change-state", "node": "n4", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "created": 1519348334.909653}
{"action": "change-state", "node": "n5", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "created": 1519348334.9331682}
{"action": "change-state", "node": "n2", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348334.934015}
{"action": "change-state", "node": "n3", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348334.9483662}
{"action": "change-state", "node": "n1", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348334.955016}
{"action": "change-state", "node": "n2", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348335.070889}
{"action": "change-state", "node": "n1", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348335.078208}
{"action": "change-state", "node": "n3", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348335.0816488}
{"action": "change-state", "node": "n4", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "created": 1519348336.030842}
{"action": "change-state", "node": "n5", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "created": 1519348336.052234}
{"action": "change-state", "node": "n5", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "created": 1519348336.084033}
{"message": "94655f46183611e88198da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n5", "created": 1519348336.084266}
{"action": "change-state", "node": "n2", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348336.1273448}
{"message": "94655f46183611e88198da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n2", "created": 1519348336.127798}
{"action": "change-state", "node": "n1", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348336.146697}
{"message": "94655f46183611e88198da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n1", "created": 1519348336.147391}
{"action": "change-state", "node": "n3", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348336.150181}
{"message": "94655f46183611e88198da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n3", "created": 1519348336.15318}
{"action": "change-state", "node": "n4", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "created": 1519348337.074358}
{"message": "94655f46183611e88198da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n4", "created": 1519348337.074653}
{"checkpoint": 0, "validators": ["n4", "n0", "n2", "n3", "n5", "n6"], "voted_nodes": ["n4", "n0", "n2", "n3", "n5"], "no_voting_nodes": ["n6"], "logger": "audit.faulty-node.no-voting", "node": "n1", "created": 1519348341.085707}
{"checkpoint": 0, "validators": ["n4", "n0", "n1", "n3", "n5", "n6"], "voted_nodes": ["n4", "n0", "n1", "n3", "n5"], "no_voting_nodes": ["n6"], "logger": "audit.faulty-node.no-voting", "node": "n2", "created": 1519348341.086303}
{"checkpoint": 0, "validators": ["n4", "n0", "n1", "n2", "n5", "n6"], "voted_nodes": ["n4", "n0", "n1", "n2", "n5"], "no_voting_nodes": ["n6"], "logger": "audit.faulty-node.no-voting", "node": "n3", "created": 1519348341.086727}
{"checkpoint": 0, "validators": ["n4", "n1", "n2", "n3", "n7", "n6"], "voted_nodes": ["n2", "n3", "n4", "n1"], "no_voting_nodes": ["n7", "n6"], "logger": "audit.faulty-node.no-voting", "node": "n5", "created": 1519348341.0871859}
{"checkpoint": 0, "validators": ["n1", "n2", "n3", "n5", "n7", "n6"], "voted_nodes": ["n2", "n3", "n5", "n1"], "no_voting_nodes": ["n7", "n6"], "logger": "audit.faulty-node.no-voting", "node": "n4", "created": 1519348342.106282}
{"action": "receive-message", "messge": "9b4e7498183611e89795da0004d06c00", "state": "ALLCONFIRM", "logger": "blockchain", "node": "n1", "created": 1519348345.2466319}
{"action": "change-state", "node": "n1", "state": {"after": "INIT", "before": "ALLCONFIRM"}, "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348345.247502}
{"liveness": "Failed", "minimum": 5, "validators": ["n0", "n1", "n2", "n3", "n4", "n5", "n6"], "faulties": "{'n6', 'n4', 'n5'}", "logger": "audit.faulty-node.no-voting", "node": "n0", "created": 1519348345.973644}
{"checkpoint": 0, "validators": ["n4", "n1", "n2", "n3", "n5", "n6"], "voted_nodes": ["n2", "n3", "n1"], "no_voting_nodes": ["n6", "n4", "n5"], "logger": "audit.faulty-node.no-voting", "node": "n0", "created": 1519348345.9742029}
{"action": "change-state", "node": "n4", "state": {"after": "INIT", "before": "ALLCONFIRM"}, "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "created": 1519348346.124923}
{"action": "change-state", "node": "n5", "state": {"after": "INIT", "before": "ALLCONFIRM"}, "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "created": 1519348346.1360068}
{"action": "change-state", "node": "n2", "state": {"after": "INIT", "before": "ALLCONFIRM"}, "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348346.220608}
{"action": "change-state", "node": "n3", "state": {"after": "INIT", "before": "ALLCONFIRM"}, "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348346.249651}
{"action": "change-state", "node": "n2", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348346.456526}
{"action": "change-state", "node": "n3", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348346.504014}
{"action": "change-state", "node": "n1", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348346.571352}
{"action": "change-state", "node": "n4", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "created": 1519348347.307155}
{"action": "change-state", "node": "n5", "state": {"after": "SIGN", "before": "INIT"}, "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "created": 1519348347.318727}
{"action": "change-state", "node": "n5", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "created": 1519348347.357696}
{"action": "change-state", "node": "n2", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348347.5595741}
{"action": "change-state", "node": "n3", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348347.611253}
{"action": "change-state", "node": "n1", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348347.649042}
{"action": "change-state", "node": "n4", "state": {"after": "ACCEPT", "before": "SIGN"}, "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "created": 1519348348.3502212}
{"action": "change-state", "node": "n4", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n4", "n1", "n2", "n3", "n5", "n6", "n7"], "logger": "consensus", "created": 1519348348.37375}
{"message": "9b4e7498183611e89795da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n4", "created": 1519348348.374041}
{"action": "change-state", "node": "n5", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n5", "n1", "n2", "n3", "n4", "n6", "n7"], "logger": "consensus", "created": 1519348348.382912}
{"message": "9b4e7498183611e89795da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n5", "created": 1519348348.383326}
{"action": "change-state", "node": "n2", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n2", "n0", "n1", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348348.593916}
{"message": "9b4e7498183611e89795da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n2", "created": 1519348348.5943282}
{"action": "change-state", "node": "n3", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n3", "n0", "n1", "n2", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348348.636193}
{"message": "9b4e7498183611e89795da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n3", "created": 1519348348.636569}
{"action": "change-state", "node": "n1", "state": {"after": "ALLCONFIRM", "before": "ACCEPT"}, "validators": ["n1", "n0", "n2", "n3", "n4", "n5", "n6"], "logger": "consensus", "created": 1519348348.68031}
{"message": "9b4e7498183611e89795da0004d06c00", "action": "save-message", "logger": "consensus", "node": "n1", "created": 1519348348.680892}
{"checkpoint": 25, "validators": ["n4", "n0", "n2", "n3", "n5", "n6"], "voted_nodes": ["n4", "n0", "n2", "n3", "n5"], "no_voting_nodes": ["n6"], "logger": "audit.faulty-node.no-voting", "node": "n1", "created": 1519348353.078707}
{"checkpoint": 22, "validators": ["n4", "n0", "n1", "n3", "n5", "n6"], "voted_nodes": ["n4", "n0", "n1", "n3", "n5"], "no_voting_nodes": ["n6"], "logger": "audit.faulty-node.no-voting", "node": "n2", "created": 1519348353.079301}
{"checkpoint": 22, "validators": ["n4", "n0", "n1", "n2", "n5", "n6"], "voted_nodes": ["n4", "n0", "n1", "n2", "n5"], "no_voting_nodes": ["n6"], "logger": "audit.faulty-node.no-voting", "node": "n3", "created": 1519348353.0919008}
{"checkpoint": 19, "validators": ["n1", "n2", "n3", "n5", "n7", "n6"], "voted_nodes": ["n2", "n3", "n5", "n1"], "no_voting_nodes": ["n7", "n6"], "logger": "audit.faulty-node.no-voting", "node": "n4", "created": 1519348353.103345}
{"checkpoint": 19, "validators": ["n4", "n1", "n2", "n3", "n7", "n6"], "voted_nodes": ["n3", "n2", "n4", "n1"], "no_voting_nodes": ["n7", "n6"], "logger": "audit.faulty-node.no-voting", "node": "n5", "created": 1519348353.1039748}

["------------------------------------"]
```

* Filtered by `liveness`
```sh
$ cat /tmp/metric_liveness.json | jq -S --indent 0 -r 'select(.liveness)' 2> /dev/null
```

> To run this bash script, we need `jq`. To install `jq`, `brew install jq`.

```json
{"liveness": "Failed", "minimum": 5, "validators": ["n0", "n1", "n2", "n3", "n4", "n5", "n6"], "faulties": "{'n6', 'n4', 'n5'}", "logger": "audit.faulty-node.no-voting", "node": "n0", "created": 1519348345.973644}
```

This will show "n0" is liveness unsafe.
