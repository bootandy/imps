from __future__ import absolute_import, division, print_function

from imps.rebuilders import GenericBuilder


def test_split_core_import():
    s = GenericBuilder(max_line_length=40, indent="    ")
    ans = s._split_core_import("import alpha.alpha.alpha, beta.beta.beta, gamma.gamma.gamma")

    output = """import (
    alpha.alpha.alpha,
    beta.beta.beta,
    gamma.gamma.gamma,
)"""
    assert ans == output


def test_split_core_import_noqa():
    s = GenericBuilder(max_line_length=40, indent="    ")
    input = "import alpha.alpha.alpha, beta.beta.beta, gamma.gamma.gamma  # NOQA"
    assert s._split_core_import(input) == input
