from __future__ import absolute_import, division, print_function

from imps.strings import get_doc_string, TRIPLE_DOUBLE, TRIPLE_SINGLE


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
    assert get_doc_string(s) == [(10, TRIPLE_DOUBLE), (29, TRIPLE_DOUBLE)]


def test_doc_string_simple():
    s = '''\"\"\" a doc string \"\"\"'''
    assert get_doc_string(s) == [(0, TRIPLE_DOUBLE), (20, TRIPLE_DOUBLE)]


def test_doc_string_with_hash():
    s = '''\"\"\" a doc string with hash # \"\"\"'''
    assert get_doc_string(s) == [(0, TRIPLE_DOUBLE), (32, TRIPLE_DOUBLE)]


def test_doc_string_not_on_newline():
    s = '''import A \"\"\"'''
    assert get_doc_string(s) == [(9, TRIPLE_DOUBLE)]


def test_doc_string_with_single_quotes():
    s = """\'\'\'import A \'\'\'"""

    assert get_doc_string(s) == [(0, TRIPLE_SINGLE), (15, TRIPLE_SINGLE)]
