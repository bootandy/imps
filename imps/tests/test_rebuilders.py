from __future__ import absolute_import, division, print_function

from imps.rebuilders import Rebuilder


def test_split_core_import():
    s = Rebuilder(max_line_length=40)
    ans = s.split_core_import("import alpha.alpha.alpha, beta.beta.beta, gamma.gamma.gamma")

    # My editor turns tabs into spaces so I can not do a literal compare
    assert 'alpha.alpha.alpha,\n' in ans
    assert 'gamma.gamma.gamma\n' in ans
    assert ans.find('import (\n') == 0
    assert ans.find(')') == len(ans) - 1


def test_split_core_import_noqa():
    s = Rebuilder(max_line_length=40)
    input = "import alpha.alpha.alpha, beta.beta.beta, gamma.gamma.gamma  # NOQA"
    assert s.split_core_import(input) == input
