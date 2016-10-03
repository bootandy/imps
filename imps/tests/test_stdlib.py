from __future__ import absolute_import, division, print_function

from imps.stdlib import get_paths, LOCAL, STDLIB, THIRDPARTY


def test_path_std():
    assert get_paths('sys') == STDLIB
    assert get_paths('io') == STDLIB
    assert get_paths('contextlib') == STDLIB


def test_path_local():
    assert get_paths('a_local_path') == LOCAL


def test_path_third():
    # Depending on how you check the module - if you unload pytest while running tests shit breaks
    assert get_paths('pytest') == THIRDPARTY
