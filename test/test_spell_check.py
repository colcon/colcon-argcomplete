# Copyright 2016-2018 Dirk Thomas
# Licensed under the Apache License, Version 2.0

from pathlib import Path

from pylint.lint import Run


spell_check_words_path = Path(__file__).parent / 'spell_check.words'


def test_spell_check():
    global spell_check_words_path
    try:
        Run([
            '--disable=all',
            '--enable=spelling',
            '--spelling-dict=en_US',
            '--ignore-comments=no',
            '--spelling-private-dict-file=' +
            str(spell_check_words_path),
            str(Path(__file__).parents[1] / 'colcon_argcomplete'),
        ] + [
            str(p) for p in
            (Path(__file__).parents[1] / 'test').glob('**/*.py')
        ])
    except SystemExit as e:
        assert not e.code, 'Some spell checking errors'
    else:
        assert False, 'The pylint API is supposed to raise a SystemExit'


def test_spell_check_word_list():
    global spell_check_words_path
    with spell_check_words_path.open('r') as h:
        lines = h.read().splitlines()
    assert lines == sorted(lines), \
        'The word list should be ordered alphabetically'
