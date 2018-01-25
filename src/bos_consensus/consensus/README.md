# (Isolated) Consensus Module

The consensus module was designed to be configurable and replaceable, so we expect that the various kind of consensus models can be integrated easily.

## How To Write New Consensus Module

`bos_consensus.consensus.isaac.py` will be the good example. Basically,

* `class ~Consensus` must be inherited from `class bos_consensus.consensus.base.BaseConsensus`

To manage clearly, the each consensus module is under directory like this,
```
bos_consensus/consensus/
    __init__.py
    base.py
    <name>_consensus.py
    ...
```
