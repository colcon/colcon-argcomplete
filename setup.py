# Copyright 2016-2018 Dirk Thomas
# Licensed under the Apache License, Version 2.0

import sys

from pkg_resources import parse_version
from setuptools import __version__ as setuptools_version
from setuptools import setup

if sys.platform == 'win32':
    print(
        "The Python package 'colcon-argcomplete' doesn't support Windows",
        file=sys.stderr)
    sys.exit(1)

setuptools_min_version = '40.5.0'
if parse_version(setuptools_version) < parse_version(setuptools_min_version):
    print(
        "The Python package 'colcon-argcomplete' requires at least setuptools "
        'version {setuptools_min_version}'.format_map(locals()),
        file=sys.stderr)
    sys.exit(1)

setup()
