from __future__ import absolute_import, division, print_function

from imps.rebuilders import Rebuilder


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
