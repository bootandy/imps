from __future__ import absolute_import, division, print_function

from imps.core import Sorter


def test_crypto_style():
    input = """from __future__ import absolute_import

import ast
import os
import sys
from functools import *
from os import path

import flake8
from flake8.defaults import *

import pytest
from pytest import *
from pytest import capture

from . import A
from . import B
from .A import A
from .B import B
from .. import A
from .. import B
from ..A import A
from ..B import B
"""

    assert Sorter('c').sort(input) == input


def test_crypto_style_handles_newlines():
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
    assert Sorter('c').sort(input) == output
