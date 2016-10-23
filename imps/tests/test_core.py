from __future__ import absolute_import, division, print_function
import pytest

from imps.core import Sorter, split_from_import


def test_base():
    input = """import X
import Y
import Z
"""
    assert Sorter().sort(input) == input


def test_base_bad_order():
    input = """import Z
import X
import Y
"""
    output = """import X
import Y
import Z
"""
    assert Sorter().sort(input) == output


def test_base_more_spaces():
    input = """import B
#A
#B
#C
import C
import A
"""
    output = """import A
import B
#A
#B
#C
import C
"""
    assert Sorter().sort(input) == output


def test_base_with_func_in():  # Maybe it shouldn't do this
    input = """import B

def my_func():
    return False

import A
"""
    output = """def my_func():
    return False

import A
import B
"""
    assert Sorter().sort(input) == output


def test_stdlib_and_local():
    input = """import io

import a_mylib
"""
    assert Sorter().sort(input) == input


def test_stdlib_and_local_bad_order():
    input = """import a_mylib
import io
"""
    output = """import io

import a_mylib
"""
    assert Sorter().sort(input) == output


def test_newlines_reduced():
    input = """import io


import sys


import A
"""
    output = """import io

import sys

import A
"""
    assert Sorter().sort(input) == output


def test_comments_between_import_types():
    input = """
import io
# A comment
import a_mylib
"""
    output = """import io

# A comment
import a_mylib
"""
    assert Sorter().sort(input) == output


def test_comments_between_import_types3():
    input = """import io

# A comment
import sys
"""
    assert Sorter().sort(input) == input


def test_comments_between_import_types4():
    input = """import io
# A comment

import sys
"""
    assert Sorter().sort(input) == input


def test_triple_quote_comments():
    input = """import A
\"\"\"Don't break my docstring \"\"\"
import B
"""
    assert Sorter().sort(input) == input


def test_triple_quote_in_a_string():
    input = """import A
s = '\"\"\"import C\"\"\"'
import B
"""
    assert Sorter().sort(input) == input


def test_triple_quote_with_newlines_and_imports_in_it():
    input = """import A

\"\"\"


ignore newlines and imports inside a giant comment


import C
\"\"\"
import B
"""
    assert Sorter().sort(input) == input


def test_triple_quotes_in_comments():
    input = """import A  # I can put these here behind a comment \"\"\"
import B
"""
    assert Sorter().sort(input) == input


def test_triple_quotes_in_string():
    input = """import A
str = '\"\"\"'
import B
"""
    assert Sorter().sort(input) == input


def test_triple_quotes_nasty():
    input = """import A
str = '\"\"\" & # are used to comment'  # \"\"\" and # are used for comments
import B
"""
    assert Sorter().sort(input) == input


def test_multiple_triple_quotes():
    input = """import A
\"\"\" ''' \"\"\" ''' \# ''' \"\"\"
 new line \"\"\"
import B
"""
    assert Sorter().sort(input) == input


def test_from_and_regular():
    input = """from __future__ import pprint

import A
from B import C
"""
    assert Sorter().sort(input) == input


def test_relative_imports():
    input = """from imps.imps import *

from . import A
from . import B
from .A import A
"""
    assert Sorter().sort(input) == input


def test_dont_remove_double_newline_before_code():
    input = """from imps.imps import *


class Style(Enum):
    SMARKETS = 1
    GOOGLE = 2
    CRYPTOGRAPHY = 3
"""
    assert Sorter().sort(input) == input


def test_reorder_from_imports():
    input = """from strings import strip_to_module_name

from enum import Enum
"""
    output = """from enum import Enum

from strings import strip_to_module_name
"""
    assert Sorter().sort(input) == output


def test_import_as():
    input = """import enum as zenum

from strings import strip_to_module_name as stripper
"""
    assert Sorter().sort(input) == input


def test_import_using_parenthesis():
    input = """from string import (
    upper as a_up,
    strip,
    find,
)
"""
    output = """from string import find, strip, upper as a_up
"""
    assert Sorter().sort(input) == output


def test_noqa_import():
    input = """import X
import Z  # NOQA
import Y
"""
    assert Sorter().sort(input) == input


def test_multiline_parentheses():
    input = """from imps.strings import (
    get_doc_string,
    strip_to_module_name, # or like this
    # We can't handle comments in an import () yet
    strip_to_module_name_from_import
)
"""
    # In future we would like to keep the comments in the correct place
    output = """# or like this
# We can't handle comments in an import () yet
from imps.strings import get_doc_string, strip_to_module_name, strip_to_module_name_from_import
"""
    assert Sorter(max_line_length=110).sort(input) == output


@pytest.mark.skip("this doesnt work yet")
def test_multiline_parentheses_with_comment():
    input = """from imps.strings import ( # A comment
    get_doc_string,
    strip_to_module_name,
)
"""
    assert Sorter(max_line_length=40).sort(input) == input


def test_multiline_slash_continue_import():
    input = """import Z, Y, \\
        X, A

def some_func(param_a, \\
param_b):
    pass
'''
def some_func(param_a, \\
param_b):
    pass
'''
"""
    output = """import A, X, Y, Z

def some_func(param_a, \\
param_b):
    pass
'''
def some_func(param_a, \\
param_b):
    pass
'''
"""
    assert Sorter().sort(input) == output


def test_triple_quotes():
    input = '''user_tracker._request_get = lambda url, verify: Mock(text="""20793353750002077:5730728,5730727
-21947406894019109:5730726,5730725""")
'''
    output = '''user_tracker._request_get = lambda url, verify: Mock(text="""20793353750002077:5730728,5730727
-21947406894019109:5730726,5730725""")
'''
    assert Sorter().sort(input) == output


def test_no_state_stays_in_sorting_object():
    """
    Sorter kept previous state at one stage causing it to always append new
    files instead of creating a new file. Dont want that happening again.
    """
    input = '''from A import B
'''
    s = Sorter()
    assert s.sort(input) == input

    input2 = '''from B import A
'''
    assert s.sort(input2) == input2


def test_underscores_in_module_names():
    input = '''from gateways.betting.gateway import *
from gateways.betting_ng.server_module import *
from gateways.bettingvery.server_module import *
'''
    assert Sorter().sort(input) == input


def test_file_begins_with_docstring_is_ok():
    input = '''"""Please don't destroy my docstring"""

from __future__ import absolute_import, division
'''
    assert Sorter().sort(input) == input


def test_split_from_import():
    assert split_from_import('from A import B') == 'from A import B'


def test_split_from_import_complex():
    assert split_from_import('from A.B   import Z,   F, W') == 'from A.B import F, W, Z'


def test_split_from_import_with_as():
    assert split_from_import('from A   import this as that,   A,Z') == 'from A import A, this as that, Z'
