# Copyright 2016-2018 Dirk Thomas
# Licensed under the Apache License, Version 2.0

import distutils.command.install as distutils_install
import inspect
import os
import shutil
import sys

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install


if sys.platform == 'win32':
    print(
        "The Python package 'colcon-argcomplete' doesn't support Windows",
        file=sys.stderr)
    sys.exit(1)

src_base = 'completion'
data_files = (
    ('share/colcon-argcomplete/hook', [
        'completion/colcon-argcomplete.bash',
        'completion/colcon-argcomplete.zsh']),
)

src_base_offset = None
dst_prefix = None
if not os.path.exists(src_base):
    # assuming this is a deb_dist build
    if os.path.exists(os.path.join('..', '..', src_base)):
        # use source base offset for data files
        for _, srcs in data_files:
            for i, src in enumerate(srcs):
                srcs[i] = os.path.join('..', '..', src)
        # use dst prefix for data files
        dst_prefix = os.path.join(
            os.getcwd(), 'debian/python3-colcon-argcomplete')


# in order to be referenced from the colcon.pkg file
# the data files need to be installed into a known fixed location
# which doesn't depend on the Python interpreter version and layout
# therefore package_data can't be used and this chunk of code is necessary
class CustomDevelopCommand(develop):

    def install_for_development(self):
        global data_files
        super().install_for_development()

        if sys.platform != 'win32':
            _foreach_data_file(
                self, data_files,
                'Creating {dst_dir} (link to {src})',
                _link_data_file)
        else:
            _foreach_data_file(
                self, data_files,
                'Copying {src} to {dst_dir}',
                _copy_data_file)

    def uninstall_link(self):
        global data_files
        super().uninstall_link()

        _foreach_data_file(
            self, data_files,
            'Removing {dst}',
            _remove_data_file)


class CustomInstallCommand(install):

    def run(self):
        global data_files
        # https://github.com/pypa/setuptools/blob/52aacd5b276fedd6849c3a648a0014f5da563e93/setuptools/command/install.py#L59-L67
        # Explicit request for old-style install?  Just do it
        if self.old_and_unmanageable or self.single_version_externally_managed:
            distutils_install.install.run(self)
        elif not self._called_from_setup(inspect.currentframe()):
            # Run in backward-compatibility mode to support bdist_* commands.
            distutils_install.install.run(self)
        else:
            super().do_egg_install()

        _foreach_data_file(
            self, data_files,
            'Copying {src} to {dst_dir}',
            _copy_data_file)


def _foreach_data_file(command, data_files, msg, callback):
    global dst_prefix
    for dst_dir, srcs in data_files:
        if command.prefix is not None:
            dst_dir = os.path.join(command.prefix, dst_dir)
        if dst_prefix:
            dst_dir = os.path.join(dst_prefix) + dst_dir
        for src in srcs:
            dst = os.path.join(dst_dir, os.path.basename(src))
            try:
                src = os.path.join(
                    os.path.dirname(os.path.realpath('setup.py')),
                    src)
            except OSError:
                pass
            print(msg.format_map(locals()))
            if not command.dry_run:
                callback(src, dst_dir, dst)


def _copy_data_file(src, dst_dir, dst):
    _prepare_destination(src, dst_dir, dst)
    shutil.copy2(src, dst_dir)


def _link_data_file(src, dst_dir, dst):
    _prepare_destination(src, dst_dir, dst)
    os.symlink(src, dst)


def _prepare_destination(src, dst_dir, dst):
    assert os.path.isfile(src), \
        "data file '{src}' not found".format_map(locals())
    assert os.path.isabs(dst_dir), \
        'Install command needs to be invoked with --prefix ' \
        'or the data files destination must be absolute'
    assert not os.path.isfile(dst_dir), \
        'data file destination directory must not be a file'
    if not os.path.isdir(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)
    try:
        os.remove(dst)
    except FileNotFoundError:
        pass


def _remove_data_file(src, dst_dir, dst):
    assert os.path.isabs(dst)
    try:
        os.remove(dst)
    except FileNotFoundError:
        pass


setup(
    cmdclass={
        'develop': CustomDevelopCommand,
        'install': CustomInstallCommand,
    },
)
