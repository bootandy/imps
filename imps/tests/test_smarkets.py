from __future__ import absolute_import, division, print_function

from imps.core import Sorter


def test_smarkets_style():
    input = '''from __future__ import absolute_import, division, print_function

import ast
import configparser
import os
import StringIO
import sys
from functools import *
from os import path

import flake8
import pytest
from flake8.defaults import NOQA_INLINE_REGEXP, STATISTIC_NAMES
from flake8.exceptions import *
from pytest import *
from pytest import capture
from pytest import compat, config

import imps
from imps import *

from . import A
from . import B
from .A import A
from .B import B
from .. import A
from .. import B
from ..A import A
from ..B import B
'''

    assert Sorter('s', 80, ['imps']).sort(input) == input


def test_smarkets_style_same_import_name():
    input = '''from __future__ import absolute_import, division, print_function

from imps.strings import AAAA
from imps.strings import TRIPLE_SINGLE
from imps.strings import get_doc_string, strip_to_module_name, strip_to_module_name_from_import
'''
# Possible alternative:
#     output = '''from __future__ import absolute_import, division, print_function
#
# from imps.strings import (
#     AAAA,
#     TRIPLE_SINGLE
#     get_doc_string,
#     strip_to_module_name,
#     strip_to_module_name_from_import
# )
# '''

    assert Sorter('s', max_line_length=110).sort(input) == input
