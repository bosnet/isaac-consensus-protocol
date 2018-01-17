import argparse
import graphviz
import json
from pprint import pprint  # noqa
import urllib.parse

from star_cluster.star_cluster import get_nodes


parser = argparse.ArgumentParser('Draw the layout of star system')
parser.add_argument('-format', default='png', help='image format', type=str, choices=graphviz.FORMATS)
parser.add_argument('-dpi', help='dpi', type=int, default=300)
parser.add_argument('-o', dest='output', required=True, help='output file', type=str)
parser.add_argument('json', help='star cluster json file', type=str)


if __name__ == '__main__':
    options = parser.parse_args()

    with open(options.json) as f:
        data = json.load(f)

    print('> star cluster:')
    pprint(data, width=10)

    quorums = dict()
    node_data = get_nodes(data)
    for name, info in node_data.items():
        quorums[name] = list()
        for i in info.validators:
            quorums[name].append(
                urllib.parse.parse_qs(urllib.parse.urlparse(i).query)['name'][0],
            )

    print('> quorums:')
    pprint(quorums)

    unary_links = dict()
    if 'unary_link' in data:
        for i in data['unary_link']:
            for j in i[0]:
                for m in i[1]:
                    unary_links[m] = j

    print('> unary links:')
    pprint(unary_links)

    connected = dict()
    quorum_names = list(quorums.keys())
    for v0 in quorum_names:
        for v1 in quorum_names:
            if v0 == v1:
                continue

            if len(set(quorums[v0]) & set(quorums[v1])) < 1:
                continue

            key = tuple(sorted((v0, v1)))
            connected[key] = set(quorums[v0]) & set(quorums[v1])

    print('> connected:')
    pprint(connected)

    g = graphviz.Digraph('G', format=options.format, engine='fdp')
    g.graph_attr.update(
        fontname='monospace', size='100,100', dpi=str(options.dpi), fontsize='10', style='rounded', splines='curved',
    )
    g.edge_attr.update(
        fontname='monospace', fontsize='6', penwidth='0.5', arrowsize='0.5', arrowhead=None, color='gray',
    )
    g.node_attr.update(
        fontname='monospace',
        fontsize='10',
        style='filled',
        color='snow',
        fontcolor='snow',
        fillcolor='crimson',
        shape='circle',
        penwidth='0'
    )

    range_count = (max(map(lambda x: len(x), connected.values())), min(map(lambda x: len(x), connected.values())))
    for key, vs in connected.items():
        arrowhead = 'normal'
        arrowtail = 'normal'

        unary = False
        if key[0] in unary_links and unary_links[key[0]] == key[1]:
            arrowhead = 'dot'
            unary = True

        if key[1] in unary_links and unary_links[key[1]] == key[0]:
            arrowtail = 'dot'
            unary = True

        count = len(vs)
        g.edge(
            *key,
            arrowsize='0.3',
            arrowhead=arrowhead,
            arrowtail=arrowtail,
            color='gray31' if unary else 'gray79',
            dir='both',
            fontcolor='gray31' if unary else 'gray79',
            label=str(count),
            penwidth='1',
        )

    g.render(options.output, cleanup=True)
