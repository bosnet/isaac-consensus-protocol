# (Isolated) Consensus Module

The consensus module was designed to be configurable and replaceable, so we expect that the various kind of consensus models can be integrated easily.

## How To Write New Consensus Module

`bos_consensus.consensus.simple_fba` will be the good example. Basically,

* The consensus module must have `class Consensus`
* `class Consensus` must be inherited from `class bos_consensus.consensus.BaseConsensus`
* the module can be accessed thru `func bos_consensus.consensus.get_consensus_module(<consensus name>)`

To manage clearly, the each consensus module is under directory like this,
```
bos_consensus/consensus/<consensus name>/
    __init__.py
    consensus.py
    ...
```
