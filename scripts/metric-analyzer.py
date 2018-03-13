import json
import math
import os
import sys
import termcolor

from bos_consensus.util import (
    ArgumentParserShowDefaults,
    logger,
)


class Printer:
    out = None

    def __init__(self, out):
        self.out = out

    def print(self, *a, **kw):
        end = kw.get('end', '\n')

        t = ' '.join(a)
        if sys.stdout.isatty() and 'color' in kw and kw['color'] is not None:
            t = termcolor.colored(t, kw['color'], attrs=kw.get('attrs'))

        self.out.write(t)
        self.out.write(end)
        self.out.flush()

        return

    def colored(self, *a, **kw):
        if not sys.stdout.isatty():
            return a[0]

        return termcolor.colored(*a, **kw)

    def line(self, c=None):
        if c is None:
            c = '-'

        self.print(c * (TERMINAL_COLUMNS - 1), color='grey', attrs=('bold',))

        return

    def head(self, s):
        self.print('# %s' % s, color='cyan')
        self.print()

    def format(self, *a, **kw):
        fmt = kw.get('fmt')
        if fmt is not None:
            t = fmt % tuple(a)
        else:
            t = ' | '.join(a)

        if kw.get('print', False):
            return self.print(t, **kw)

        return t


class FaultyNodeHistory:
    history = None

    def __init__(self):
        self.history = dict()
        self.created_times = dict()

    def add(self, node, created_time, reason):
        self.history.setdefault(node, list())
        self.history[node].append(dict(
            created_time=created_time,
            reason=reason,
        ))
        self.created_times.setdefault(created_time, list())
        self.created_times[created_time].append(dict(node=node, reason=reason))

        return

    def get(self, *a):
        return self.history.get(*a)

    def get_by_time(self, node, t):
        if node not in self:
            return None

        if t not in self.created_times:
            return None

        for i in self.created_times[t]:
            if i['node'] == node:
                return i

        return None

    def get_by_close_time(self, node, started, ended):
        if node not in self:
            return None

        found = list()
        for i in self.get(node):
            if started > i['created_time']:
                continue

            if ended < i['created_time']:
                continue

            found.append(i)

        return found

    def __contains__(self, a):
        return a in self.history

    def __len__(self):
        return len(self.history)

    def __iter__(self):
        return self.history.keys().__iter__()

    def __and__(self, a):
        return set(self.history.keys()) & a

    def __rand__(self, a):
        return a & set(self.history.keys())


class BaseAnalyzer:
    messages = None
    start_time = None
    faulty_node_history = None
    filtered_nodes = None

    def __init__(self, filtered_nodes, messages):
        self.filtered_nodes = filtered_nodes
        self.messages = messages

        self.start_time = self.messages[0]['created']

        self.faulty_node_history = FaultyNodeHistory()

    def analyze(self):
        raise NotImplementedError()


class NodesHistoryAnalyzer(BaseAnalyzer):
    nodes = None

    def __init__(self, *a, **kw):
        super(NodesHistoryAnalyzer, self).__init__(*a, **kw)

        nodes = dict()
        for i in self.messages:
            nodes.setdefault(i['node'], list())
            nodes[i['node']].append(i)

        self.nodes = nodes
        log.debug('found %d nodes: %s', len(self.nodes.keys()), sorted(self.nodes.keys()))

    def analyze(self):
        PRINTER.head('node history')

        for message in self.messages:
            if message.get('action') not in ('faulty-node',):
                continue

            self.faulty_node_history.add(message['node'], message['created'], message['fault_type'])

        for node, messages in self.nodes.items():
            if len(self.filtered_nodes) > 0 and node not in self.filtered_nodes:
                continue

            node_history_analyzer = NodeHistoryAnalyzer(self, node, self.filtered_nodes, messages)
            node_history_analyzer.analyze()

        return


class NodeHistoryAnalyzer(BaseAnalyzer):
    nodes_analyzer = None
    node = None
    messaegs = None
    messaeg_ids = None
    is_faulty_node = None
    connected_validators = None

    def __init__(self, nodes_analyzer, node, *a, **kw):
        assert isinstance(nodes_analyzer, NodesHistoryAnalyzer)

        super(NodeHistoryAnalyzer, self).__init__(*a, **kw)

        self.node = node
        self.message_ids = dict()
        self.nodes_analyzer = nodes_analyzer
        self.is_faulty_node = False
        self.connected_validators = list()

    def analyze(self):
        PRINTER.print('## %s' % self.node, end='\n\n')

        PRINTER.line('=')

        connected_validators = set()
        for m in self.messages:
            if m.get('action') != 'connected':
                continue

            connected_validators = connected_validators.union(m['validators'])

        self.connected_validators = connected_validators

        message_ids = dict()
        for message in self.messages:
            message_id = None
            if 'message' in message:
                message_id = message['message']
            elif 'ballot' in message:
                message_id = message['ballot']['ballot_id']

            if message_id is None or message_id in message_ids:
                continue

            message_ids[message_id] = 'm%d' % len(message_ids)

        self.message_ids = message_ids

        max_length_message_ids = max(map(len, self.message_ids.values()))
        for i, (message_id, message_name) in enumerate(self.message_ids.items()):
            PRINTER.format(
                ' ' * 10,
                '%17s' % '* message:',
                message_name,
                ('%%%ds' % max_length_message_ids) % message_id,
                print=True,
            )
            PRINTER.line('=' if i == len(self.message_ids) - 1 else '-')

        all_faulty_nodes = connected_validators & self.nodes_analyzer.faulty_node_history
        faulty_nodes = list()
        for i, m in enumerate(self.messages):
            if 'action' not in m:
                continue

            if i > 0 and len(all_faulty_nodes) > 0:
                newly_found = None
                for f in all_faulty_nodes:
                    if f == self.node:
                        continue

                    c = self.nodes_analyzer.faulty_node_history.get_by_close_time(
                        f,
                        self.messages[i - 1]['created'],
                        self.messages[i - 1]['created'],
                    )
                    if c is None or len(c) < 1:
                        continue

                    newly_found = c[0]
                    faulty_nodes.append(f)

                if newly_found is not None:
                    self._check_health(faulty_nodes, newly_found)

            self.format(m)

            PRINTER.line('-' if i < len(self.messages) - 2 else '=')

        PRINTER.print()

        return

    def format(self, message):
        if 'action' not in message:
            return

        fn = getattr(self, '_format_%s' % message['action'].replace('-', '_'), None)
        if fn is None:
            log.error('unknown action, "%s" found: %s', message['action'], message)

            return

        m = fn(message)
        if m is None:
            return

        self._format(message, m)
        return

    def _format(self, message, m):
        message_id = ' ' * max(map(len, self.message_ids.values()))
        if 'message' in message:
            message_id = message['message']
        elif 'ballot' in message:
            message_id = message['ballot']['ballot_id']

        d = '%0.3f' % (message['created'] - self.start_time)
        PRINTER.format(
            '%10s' % d,
            '%17s' % message['action'],
            self.message_ids.get(message_id, message_id),
            m,
            print=True,
        )

        return

    def get_node_name(self, node):
        return '%s%s' % (node, '*' if node == self.node else '')

    def _format_change_state(self, message):
        s = '%s -> %s' % (
            termcolor.colored(message['state']['after'], 'yellow'),
            termcolor.colored(
                message['state']['after'],
                'green' if message['state']['after'] in ('ALLCONFIRM',) else 'yellow',
            ),
        )

        return '%s' % s

    def _format_connected(self, message):
        target = message['target']
        if target == message['node']:
            target = 'self'

        return target

    def _format_receive_message(self, message):
        return 'from=client'

    def _format_receive_ballot(self, message):
        return PRINTER.format(
            'from=%-4s' % self.get_node_name(message['ballot']['node_name']),
            self._make_ballot_state(message),
            'ballot=%s' % message['ballot']['ballot_id'],
        )

    def _make_ballot_state(self, message):
        return 'ballot state=%-6s' % message['ballot']['state']

    def _format_save_message(self, message):
        return ''

    def _format_faulty_node(self, message):
        if self.nodes_analyzer.faulty_node_history.get_by_time(message['node'], message['created']) is None:
            return

        t = '%10s' % (message['fault_type'])
        if message['fault_type'] == 'no_voting':
            t = PRINTER.format(
                t,
                'from=%-4s' % self.get_node_name(message['ballot']['node_name']),
                self._make_ballot_state(message),
            )
        elif message['fault_type'] == 'state_regression':
            t = PRINTER.print(
                t,
                '%s -> %s' % (
                    message['ballot']['node_name'],
                    message['target'],
                ),
                'ballot state: %s -> %s' % (
                    message['state']['before'],
                    message['state']['after'],
                ),
            )
        elif message['fault_type'] == 'node_unreachable':
            t = PRINTER.format(
                t,
                'node=%s' % message['node'],
            )

        return t

    def _format_removed(self, message):
        return PRINTER.format(
            message['target'],
            'validators=%s' % message['validators'],
        )

    def _format_receive_new_ballot(self, message):
        return PRINTER.format(
            'from=%-4s' % self.get_node_name(message['ballot']['node_name']),
            self._make_ballot_state(message),
            'ballot state=%s' % message['ballot']['state'],
            'ballot result=%s' % message['ballot']['result'],
        )

    def _format_store_ballot(self, message):
        return PRINTER.format(
            'from=%-4s' % self.get_node_name(message['ballot']['node_name']),
            self._make_ballot_state(message),
            'ballot state=%s' % message['ballot']['state'],
            'ballot result=%s' % message['ballot']['result'],
        )

    def _check_health(self, faulty_nodes, info):
        message = dict(
            action='faulty-node-found',
            created=info['created_time'],
        )
        self._format(
            message,
            PRINTER.format(str(faulty_nodes), 'reason=%s' % info['reason']),
        )

        return


class FaultToleranceAnalyzer(BaseAnalyzer):
    connected = list()

    def __init__(self, *a, **kw):
        super(FaultToleranceAnalyzer, self).__init__(*a, **kw)

        self.connected = dict()

    def analyze(self):
        PRINTER.head('fault tolerance')

        # get the largest connected validators set
        connected = dict()
        for m in self.messages:
            if m.get('action') in ('faulty-node',):
                self.faulty_node_history.add(m['node'], m['created'], m['fault_type'])

            if m.get('action') != 'connected':
                continue

            node = m['node']
            connected.setdefault(node, set())
            connected[node] = connected[node].union(m['validators'])

        self.connected = connected

        for node, validators in self.connected.items():
            if len(self.filtered_nodes) > 0 and node not in self.filtered_nodes:
                continue

            PRINTER.print('## %s' % (node,), end='\n\n', color='white', attrs=('bold',))

            PRINTER.line('=')
            qa = '%-40s' % sorted(self.connected[node])

            PRINTER.print(PRINTER.format('validators', qa, fmt='* %14s | %s'))
            PRINTER.line('=')
            self._format(1, self.connected[node])
            PRINTER.line()
            self._format(math.ceil((len(self.connected[node]) - 1) / 3), self.connected[node], prefix='max')
            PRINTER.line('=')
            PRINTER.print()

        return

    def _format(self, f, validators, prefix=None):
        if prefix is None:
            prefix = 'min'

        is_safe = len(validators) >= (3 * f + 1)
        PRINTER.print(
            PRINTER.format(
                '%s f=%s' % (prefix, f),
                '3f + 1 >= nodes',
                '3 * %d + 1 = %d <= %d' % (
                    f,
                    3 * f + 1,
                    len(validators),
                ),
                is_safe,
                fmt='%16s | %s | %s | is safe=%s',
            ),
            color=None if is_safe else 'red',
        )

        return


class HealthAnalyzer(BaseAnalyzer):
    node_connected_validators = None

    def __init__(self, *a, **kw):
        super(HealthAnalyzer, self).__init__(*a, **kw)

        self.connected = dict()
        self.node_pairs = list()

    def analyze(self):
        # get the largest connected validators set
        connected = dict()
        for m in self.messages:
            if m.get('action') in ('faulty-node',):
                self.faulty_node_history.add(m['node'], m['created'], m['fault_type'])

            if m.get('action') != 'connected':
                continue

            node = m['node']
            connected.setdefault(node, set())
            connected[node] = connected[node].union(m['validators'])

        self.connected = connected

        for node, validators in self.connected.items():
            log.debug('found %d validators for %s: %s', len(validators), node, sorted(validators))

        # guessing quorums
        node_pairs = list()
        all_nodes = self.connected.keys()
        for a in all_nodes:
            for b in all_nodes:
                if a == b:
                    continue

                commons = set(self.connected[a]) & set(self.connected[b])
                if len(commons) < 1:
                    continue

                pair = sorted([a, b])
                if pair in node_pairs:
                    continue

                node_pairs.append(pair)

        self.node_pairs = node_pairs

        return


class SafetyAnalyzer(HealthAnalyzer):
    def analyze(self):
        PRINTER.head('quorums safety')

        super(SafetyAnalyzer, self).analyze()

        # check safety
        for pair in self.node_pairs:
            if len(self.filtered_nodes) > 0 and len(set(pair) & set(self.filtered_nodes)) < 1:
                continue

            self._format_node(pair)
            PRINTER.line('=')
            PRINTER.print()

    def _format_node(self, pair):
        a, b = pair

        prefix = '%s <-> %s' % (a, b)
        PRINTER.print('##', prefix, end='\n\n')

        PRINTER.line('=')

        qa = '%-40s' % sorted(self.connected[a])
        qb = '%s' % sorted(self.connected[b])

        PRINTER.format(a, qa, print=True, color='yellow', fmt='* %12s | %s')
        PRINTER.line()
        PRINTER.format(b, qb, print=True, color='yellow', fmt='* %12s | %s')
        PRINTER.line()

        commons = set(self.connected[a]) & set(self.connected[b])

        PRINTER.format('commons', sorted(commons), print=True, color='yellow', fmt='* %12s | %s')
        PRINTER.line()

        faulty_nodes = sorted(self.faulty_node_history & commons)
        PRINTER.format(
            'faulty nodes',
            faulty_nodes if len(faulty_nodes) > 0 else '-',
            print=True,
            color='yellow',
            fmt='* %12s | %s',
        )
        PRINTER.line()

        self._format(1, a, b)

        if len(commons) > 1:
            PRINTER.line()
            self._format(len(commons), a, b, prefix='max')

        if len(self.faulty_node_history & commons) > 0:
            PRINTER.line()
            f = len(self.faulty_node_history & commons)
            self._format(f, a, b, prefix='happened')

        return

    def _format(self, f, a, b, prefix=None):
        if prefix is None:
            prefix = 'min'

        commons = set(self.connected[a]) & set(self.connected[b])
        is_safe = len(commons) - 1 >= f

        PRINTER.format(
            '%s f=%d' % (prefix, f),
            'commons - 1 >= f',
            '%d - 1 = %d >= %d' % (
                len(commons),
                len(commons) - 1,
                f,
            ),
            'safety=%-5s' % is_safe,
            color='green' if is_safe else 'red',
            fmt='%14s | %s | %-15s | %s',
            print=True,
        )

        return


PRINTER = Printer(sys.stdout)

ANALYZERS = {
    'history': NodesHistoryAnalyzer,
    'safety': SafetyAnalyzer,
    'fault-tolerance': FaultToleranceAnalyzer,
}


try:
    _, TERMINAL_COLUMNS = os.popen('stty size', 'r').read().split()
except ValueError:
    TERMINAL_COLUMNS = 0
else:
    TERMINAL_COLUMNS = int(TERMINAL_COLUMNS)

parser = ArgumentParserShowDefaults()

log = None
logger.set_argparse(parser)

parser.add_argument(
    '-type',
    help='set the analyzer type to be shown (%s)' % ANALYZERS.keys(),
    type=str,
)

parser.add_argument(
    '-nodes',
    help='set the nodes to be shown',
    type=str,
)

parser.add_argument(
    'metric',
    help='metric file',
    type=str,
)

if __name__ == '__main__':
    options = parser.parse_args()
    logger.from_argparse(logger, options)
    log = logger.get_logger(__name__)

    log.debug('options: %s', options)

    types = list(filter(lambda x: len(x.strip()) > 0, options.type.split(',') if options.type else list()))
    if len(types) > 0:
        invalids = set(types) - set(ANALYZERS.keys())
        if len(invalids) > 0:
            parser.error('invalid type: %s' % sorted(invalids))

    if len(types) < 1:
        types = ANALYZERS.keys()

    log.debug('types: %s', types)

    filtered_nodes = list(filter(lambda x: len(x.strip()) > 0, options.nodes.split(',') if options.nodes else list()))
    log.debug('filtered nodes: %s', filtered_nodes)

    all_messages = list()
    for i in open(options.metric):
        o = json.loads(i)

        all_messages.append(o)

    log.debug('%d metric messages parsed', len(all_messages))

    for i in types:
        ANALYZERS[i](filtered_nodes, all_messages).analyze()

    sys.exit(0)
