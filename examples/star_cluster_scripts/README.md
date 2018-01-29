# Quorum Intersection Test In Single Process

## Run Quorum Topology Server Example

```
$ cd examples/star_cluster_scripts
$ python run-star-cluster.py -i star_cluster_conf.json -log-level debug
```

## Run Quorum Nodes Ini Files Generator Example

```
$ cd examples/star_cluster_scripts
$ python star_cluster_ini_generator.py -i star_cluster_conf.json -o outdir
```


## Input Json File Format

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


## Input Json File Example
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

## Example's Output Node Validators

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

## Verifing The Layout Of Star System

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
