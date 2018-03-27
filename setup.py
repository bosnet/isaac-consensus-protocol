import sys  # noqa
import subprocess  # noqa
from pip.req import parse_requirements
from setuptools import setup, find_packages


commit = subprocess.Popen(
    'git rev-parse --short HEAD'.split(),
    stdout=subprocess.PIPE,
).stdout.read().decode('utf-8').strip()

install_reqs = parse_requirements('requirements.txt', session='')

setup(
    name='bosnet-prototype-fba',
    version='0.1+%s' % commit,
    description='simulation for fba consensus protocol',
    author='BOSNet team',
    license='GPLv3+',
    keywords='bosnet blockchainos blockchain fba stellar quorum python byzantine agreement',
    zip_safe=False,
    install_requires=list(map(lambda x: str(x.req), install_reqs)),
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=('test',)),
    scripts=(
        'scripts/run-blockchain.py',
        'scripts/run-client.py',
        'scripts/run-client-new.py',
        'scripts/send-message.py',
        'scripts/metric-analyzer.py',
        'examples/experiment/run-consensus-performance.py',
    ),
)
