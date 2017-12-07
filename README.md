# FBA Prototype Of BOSNet

Validate the consensus model of the FBA

## Technical Stacks

- Written in Python
- HTTP-based Messaging
- Simple and In-Memory Storage
- etc.

## Features

- Command Line Interface
- Consensus
- Networking

## Non-functional requirements

### Performance
- Scale-up

### User Experience

- Simple Configuration

### Code Quality
- TDD

### Logging System

## Installation

To install and deploy the source, you need to install these packages,

 - python: 3.5 or higher
 - pip

```
$ pip install virtualenv
$ virtualenv bosnet-prototype-fba
$ cd bosnet-prototype-fba
$ source bin/activate
$ mkdir src/
$ cd src
$ git clone git@github.com:owlchain/bosnet-prototype-fba.git
$ cd bosnet-prototype-fba
$ pip install -r requirements.txt
```

## Deployment

```
$ cd bosnet-prototype-fba/bos-consensus
$ python run_node.py node5001.ini
2017-12-06 15:21:48,459 - __main__ - DEBUG - Node ID: 5001
2017-12-06 15:21:48,459 - __main__ - DEBUG - Node PORT: 5001
2017-12-06 15:21:48,459 - __main__ - DEBUG - Validators: ['localhost:5002', 'localhost:5003']
```

Run the other nodes like this.
```
$ python run_node.py node5002.ini
$ python run_node.py node5003.ini
```
