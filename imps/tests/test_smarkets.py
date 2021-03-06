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

from common.interfaces import Config
from common.rest.decorators import jsonify
from han.db import Database
from winners.server.db_access import (
    acknowledge_winner_exposure_for_market,
    get_acknowledged_winner_exposures_for_market,
)

from . import A
from . import B
from .A import A
from .B import B
from .. import A
from .. import B
from ..A import A
from ..B import B
'''

    assert Sorter('s', 80, ['common', 'winners', 'han']).sort(input) == input


def test_smarkets_style_from_import_capitals_are_not_lowered():
    input = '''from __future__ import absolute_import, division, print_function

from imps.strings import AAAA
from imps.strings import get_doc_string, strip_to_module_name, strip_to_module_name_from_import
from imps.strings import ZZZZ
'''
# Possible alternative:
#     output = '''from __future__ import absolute_import, division, print_function
#
# from imps.strings import (
#     AAAA,
#     get_doc_string,
#     strip_to_module_name,
#     strip_to_module_name_from_import
#     ZZZZ,
# )
# '''

    assert Sorter('s', max_line_length=110).sort(input) == input


def test_newlines_reduced():
    s = Sorter('s', 80, ['local'])
    input = """import io


import sys


import A
"""
    output = """import io
import sys

import A
"""
    assert s.sort(input) == output


def test_no_new_line_between_same_type():
    s = Sorter(type='s', max_line_length=110, indent="    ")
    input_str = """
from __future__ import absolute_import, division, print_function

import re

from collections import OrderedDict
"""
    correct = """from __future__ import absolute_import, division, print_function

import re
from collections import OrderedDict
"""
    assert s.sort(input_str) == correct
