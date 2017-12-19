# FBA Flow Simulation

## Run

```
$ python run.py -h
usage: run.py [-h] [-s] [-nodes NODES]

optional arguments:
  -h, --help    show this help message and exit
  -s            turn off the debug messages
  -nodes NODES  number of validator nodes in the same quorum
```

```
$ python run.py -s
```

The number of nodes(validators) can be set, by default, 4.

```
$ python run.py -s -nodes 10
```
