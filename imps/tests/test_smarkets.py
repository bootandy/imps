from __future__ import absolute_import, division, print_function

from imps.core import Sorter, Style


def test_smarkets_style():
    input = '''from __future__ import absolute_import, division, print_function

import ast
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

from . import A
from . import B
from .A import A
from .B import B
from .. import A
from .. import B
from ..A import A
from ..B import B
'''

    assert Sorter(Style.SMARKETS).sort(input) == input
