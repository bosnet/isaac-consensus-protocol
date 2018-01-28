# FBA Prototype Of BOSNet

Validate the consensus model of the FBA

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
```

```
$ python setup.py develop
```

## Deployment

```
$ run-blockchain.py -h
usage: run-blockchain.py [-h] [-verbose]
                         [-log-level {critical,fatal,error,warn,warning,info,debug}]
                         [-log-output LOG_OUTPUT]
                         [-log-output-metric LOG_OUTPUT_METRIC]
                         [-log-show-line] [-log-no-color]
                         conf

positional arguments:
  conf                  ini config file for server node

optional arguments:
  -h, --help            show this help message and exit
  -verbose              verbose log (default: False)
  -log-level {critical,fatal,error,warn,warning,info,debug}
                        set log level (default: debug)
  -log-output LOG_OUTPUT
                        set log output file (default: None)
  -log-output-metric LOG_OUTPUT_METRIC
                        set metric output file (default: None)
  -log-show-line        show seperate lines in log (default: False)
  -log-no-color         disable colorized log message by level (default:
                        False)
```

### Running Node Server

Set the config file.
```
$ run-blockchain.py examples/node5001.ini
2017-12-06 15:21:48,459 - __main__ - DEBUG - Node ID: 5001
2017-12-06 15:21:48,459 - __main__ - DEBUG - Node PORT: 5001
2017-12-06 15:21:48,459 - __main__ - DEBUG - Validators: ['localhost:5002', 'localhost:5003']
```

Run the other nodes like this.
```
$ python run-blockchain.py examples/node5002.ini
$ python run-blockchain.py examples/node5003.ini
```

### Running Message Client, `run-client.py`

```
$ run-client.py  -h
usage: run-client.py [-h] [-verbose]
                     [-log-level {critical,fatal,error,warn,warning,info,debug}]
                     [-log-output LOG_OUTPUT]
                     [-log-output-metric LOG_OUTPUT_METRIC] [-log-show-line]
                     [-log-no-color] [-m MESSAGE] [-i IP] [-p PORT]

optional arguments:
  -h, --help            show this help message and exit
  -verbose              verbose log (default: False)
  -log-level {critical,fatal,error,warn,warning,info,debug}
                        set log level (default: debug)
  -log-output LOG_OUTPUT
                        set log output file (default: None)
  -log-output-metric LOG_OUTPUT_METRIC
                        set metric output file (default: None)
  -log-show-line        show seperate lines in log (default: False)
  -log-no-color         disable colorized log message by level (default:
                        False)
  -m MESSAGE, --message MESSAGE
                        Messages you want to send to the server (default:
                        Quaerat)
  -i IP, --ip IP        Server IP you want to send the message to (default:
                        localhost)
  -p PORT, --port PORT  Server port you want to send the message to (default:
                        5001)
```

After checking node state in cmd line, then run client like this.
Send one message to `5001`
```
$ python scripts/run-client.py --ip "localhost" --port 5001 --message "message"
```

Send five messages at a time every 4 seconds to `5001`
```
for i in $(seq 5)
do
    python scripts/run-client.py \
        --ip localhost \
        --port 5001 \
        --message "message-$i"
        sleep 4
done
```

Send five messages at a time every 4 seconds to `5001` and` 5002`,
```
for port in 5001 5002
do
    for i in $(seq 5)
    do
        python scripts/run-client.py \
            --ip localhost \
            --port $port \
            --message "message-$i"
            sleep 4
    done
done
```

Send five messages at a time every 4 seconds to `5000-5003` randomly three times
```
for _ in $(seq 3)
do
    p=$(expr $RANDOM % 4)
    for i in $(seq 5)
    do
        python scripts/run-client.py \
            --ip localhost \
            --port "500$p" \
            --message "message-$i"
            sleep 4
    done
done
```

## Test

```
$ cd bosnet-prototype-fba
$ pytest
```

## Examples

### Quorum Intersection Test In Single Process

#### Run Quorum Topology Server Example

```
$ cd examples/star_cluster_scripts
$ python run-star-cluster.py -i star_cluster_conf.json -debug
```

#### Run Quorum Nodes Ini Files Generator Example

```
$ cd examples/star_cluster_scripts
$ python star_cluster_ini_generator.py -i star_cluster_conf.json -o outdir
```


#### Input Json File Format

```
{
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
    ]
}
```


#### Input Json File Example
```json
{
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
            "threshold": 80,
            "faulty_percent": 20,
            "faulty_kind": "node_unreachable"
        },
        "n4":
        {
            "faulty_percent": 20
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
    ]
}
```

#### Example's Output Node Validators

```
N1: (N2, N3)
N2: (N1, N3)
N3: (N1, N2, N8, N9)
N4: (N5, N6, N7, N8)
N5: (N4, N6, N7)
N6: (N4, N5, N7, N9)
N7: (N4, N5, N6)
N8: (N3, N4)
N9: (N1, N3, N6)
```

#### Verifing The Layout Of Star System

To eveything work properly, install `graphviz` first.

```
$ pip install -r requirements.txt
```

For Mac

```
$ brew install graphviz
```

```
$ cd examples/star_cluster_scripts/
$ python draw-star-system.py -h
usage: Draw the layout of star system [-h]
                                      [-format {webp,gif,wbmp,xdot1.2,gtk,dot,ismap,pct,ico,json0,cgimage,gv,svg,tk,png,gd,canon,json,imap_np,pov,cmap,pic,tiff,xdot,jpe,jpg,psd,jp2,tga,cmapx_np,vmlz,xdot1.4,vml,xdot_json,dot_json,jpeg,plain-ext,sgi,bmp,pict,eps,exr,svgz,x11,gd2,xlib,plain,ps2,pdf,tif,imap,fig,cmapx,vrml,ps}]
                                      [-dpi DPI] -o OUTPUT
                                      json

positional arguments:
  json                  star cluster json file

optional arguments:
  -h, --help            show this help message and exit
  -format {webp,gif,wbmp,xdot1.2,gtk,dot,ismap,pct,ico,json0,cgimage,gv,svg,tk,png,gd,canon,json,imap_np,pov,cmap,pic,tiff,xdot,jpe,jpg,psd,jp2,tga,cmapx_np,vmlz,xdot1.4,vml,xdot_json,dot_json,jpeg,plain-ext,sgi,bmp,pict,eps,exr,svgz,x11,gd2,xlib,plain,ps2,pdf,tif,imap,fig,cmapx,vrml,ps}
                        image format
  -dpi DPI              dpi
  -o OUTPUT             output file
```

```
$ python draw-star-system.py -format png -o /tmp/first-shot star_cluster_conf.json
$ ls -al /tmp/*.png
-rw-r--r--  1 spikeekips  wheel  162773 Jan 11 15:23 /tmp/first-shot.png
$ open /tmp/first-shot.png
```
