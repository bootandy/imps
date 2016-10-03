from __future__ import absolute_import, division, print_function
from imps.core import split_from_import


def test_split_from_import():
    assert split_from_import('from A import B') == 'from A import B'


def test_split_from_import_complex():
    assert split_from_import('from A.B   import Z,   F, W') == 'from A.B import F, W, Z'
