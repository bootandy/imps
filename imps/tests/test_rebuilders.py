from __future__ import absolute_import, division, print_function

from imps.rebuilders import Rebuilder, sorter


def test_split_core_import():
    s = Rebuilder(max_line_length=40)
    ans = s.split_core_import("import alpha.alpha.alpha, beta.beta.beta, gamma.gamma.gamma")

    output = """import (
    alpha.alpha.alpha,
    beta.beta.beta,
    gamma.gamma.gamma,
)"""
    assert ans == output


def test_split_core_import_noqa():
    s = Rebuilder(max_line_length=40)
    input = "import alpha.alpha.alpha, beta.beta.beta, gamma.gamma.gamma  # NOQA"
    assert s.split_core_import(input) == input


def test_sorter():
    assert sorter("""from a import B, C""") == 'from a import b, c'


def test_sorter_with_complex_from_import():
    assert sorter("""from a import ( # hello
    B, # hi
    C
)""") == 'from a import b, c'
