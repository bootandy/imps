from __future__ import absolute_import, division, print_function

import pytest

from imps.shell import normalize_file_name


def test_normalize_file_name():
    assert normalize_file_name('tox.ini') == 'tox.ini'
    assert normalize_file_name('tox.ini:34:144') == 'tox.ini'


    assert normalize_file_name('bad_path.nothing') is None
