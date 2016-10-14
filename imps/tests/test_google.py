from __future__ import absolute_import, division, print_function

from imps.core import Sorter, Style


def test_google_style():
    input = """from __future__ import absolute_import

import ast
from functools import *
import os
from os import path
import StringIO
import sys

import flake8
from flake8.defaults import *

import pytest
from pytest import *
from pytest import capture
from pytest import compat, Config

from . import A
from . import B
from .A import A
from .B import B
from .. import A
from .. import B
from ..A import A
from ..B import B
"""
    assert Sorter(Style.GOOGLE).sort(input) == input


def test_google_style_handles_newlines():
    input = """from __future__ import absolute_import
import pytest
import enum

import ast

import os
"""
    output = """from __future__ import absolute_import

import ast
import enum

import os

import pytest
"""
    assert Sorter(Style.GOOGLE).sort(input) == output
