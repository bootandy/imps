from __future__ import absolute_import, division, print_function
from imps.core import Sorter, Style


def test_smarkets_style():
    input = '''from __future__ import absolute_import

import ast
import os
import StringIO
import sys
from functools import *
from os import path

import pytest
from pytest import *
from pytest import capture
from pytest import compat, config

import imps
from imps.imps import *

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
