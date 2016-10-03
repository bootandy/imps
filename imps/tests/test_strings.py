from __future__ import absolute_import, division, print_function

from imps.strings import get_doc_string, strip_to_module_name, strip_to_module_name_from_import


def test_strip_to_module_name():
    assert strip_to_module_name('import io') == 'io'
    assert strip_to_module_name('import fishsticks') == 'fishsticks'
    assert strip_to_module_name('import fish.sticks.thing ') == 'fish.sticks.thing'
    assert strip_to_module_name('import fishsticks # a comment') == 'fishsticks'


def test_strip_to_module_name_from_import():
    assert strip_to_module_name_from_import('from io import *') == 'io'
    assert strip_to_module_name_from_import('from fishsticks import a,b') == 'fishsticks'
    assert strip_to_module_name_from_import('from fish.sticks.thing import that') == 'fish.sticks.thing'


def test_doc_string_ignores_normal_line():
    s = 'import A'
    assert not get_doc_string(s)


def test_doc_string_ignores_doc_string_in_comment():
    s = 'import A  # triple comment \"\"\" '
    assert not get_doc_string(s)


def test_doc_string_ignores_strings():
    s = '''s = '\"\"\"' '''
    assert not get_doc_string(s)


def test_doc_string_gets_data_after_a_string():
    s = '''s = '\"\"\"' \"\"\" after a str \"\"\" '''
    assert get_doc_string(s) == [10, 26]


def test_doc_string_simple():
    s = '''\"\"\" a doc string \"\"\"'''
    assert get_doc_string(s) == [0, 17]


def test_doc_string_with_hash():
    s = '''\"\"\" a doc string with hash # \"\"\"'''
    assert get_doc_string(s) == [0, 29]


def test_doc_string_not_on_newline():
    s = '''import A \"\"\"'''
    assert get_doc_string(s) == [9]
