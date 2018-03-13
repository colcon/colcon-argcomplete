# Copyright 2016-2018 Dirk Thomas
# Licensed under the Apache License, Version 2.0

from colcon_argcomplete.argcomplete_completer import get_argcomplete_completer
from colcon_argcomplete.argument_parser.argcomplete.completer.package_name \
    import package_name_completer
from colcon_core.argument_parser import ArgumentParserDecorator
from colcon_core.argument_parser import ArgumentParserDecoratorExtensionPoint
from colcon_core.plugin_system import satisfies_version


class ArgcompleteArgumentParserDecorator(
    ArgumentParserDecoratorExtensionPoint
):
    """Argcomplete-based completions for the command line tool."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            ArgumentParserDecoratorExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def decorate_argument_parser(self, *, parser):  # noqa: D102
        return ArgcompleteDecorator(parser)


class ArgcompleteDecorator(ArgumentParserDecorator):
    """Attach completers to some known arguments."""

    def __init__(self, parser):  # noqa: D107
        # avoid setting members directly, the base class overrides __setattr__
        # pass them as keyword arguments instead
        super().__init__(parser)

    def add_argument(self, *args, **kwargs):  # noqa: D102
        argument = self._parser.add_argument(*args, **kwargs)

        completer = get_argcomplete_completer(self._parser, *args, **kwargs)
        if completer is not None:
            argument.completer = completer

        elif '--log-level' in args:
            try:
                from argcomplete.completers import ChoicesCompleter
            except ImportError:
                pass
            else:
                argument.completer = \
                    ChoicesCompleter(
                        ('critical', 'error', 'warning', 'info', 'debug'))

        elif kwargs.get('metavar') == 'PKG_NAME':
            argument.completer = package_name_completer

        return argument

    def parse_args(self, *args, **kwargs):
        """Register argcomplete hook."""
        from argcomplete import autocomplete
        autocomplete(self._parser)
        return self._parser.parse_args(*args, **kwargs)
