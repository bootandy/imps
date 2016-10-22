from __future__ import absolute_import, division, print_function

from imps.stdlib import get_paths, LOCAL, STDLIB, strip_to_first_module, THIRDPARTY


def test_strip_to_first_module():
    assert strip_to_first_module('from alpha.beta import squid') == 'alpha'
    assert strip_to_first_module('import sys') == 'sys'
    assert strip_to_first_module('import sys, io') == 'sys'
    assert strip_to_first_module('from sys import stdin') == 'sys'
    assert strip_to_first_module('from . import A') == '.'
    assert strip_to_first_module('from ..B import A') == '..B'


def test_path_std():
    assert get_paths('import sys', []) == STDLIB
    assert get_paths('import io', []) == STDLIB
    assert get_paths('from contextlib import *', []) == STDLIB


def test_path_local():
    assert get_paths('import a_local_path', ['a_local_path']) == LOCAL
    assert get_paths('import a_local_path.submodule', ['a_local_path']) == LOCAL


def test_path_third():
    assert get_paths('import pytest', []) == THIRDPARTY
    assert get_paths('import flask.abort', []) == THIRDPARTY
    assert get_paths('fom six import sax', []) == THIRDPARTY
