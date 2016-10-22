from __future__ import absolute_import, division, print_function

import re

from flake8_import_order import STDLIB_NAMES


FUTURE = 0
STDLIB = 1
THIRDPARTY = 2
LOCAL = 3
RELATIVE = -1


def strip_to_first_module(imp):
    imp = re.sub(r'^from\s+', '', imp)
    imp = re.sub(r'^import\s+', '', imp)
    if imp.find('.') == 0:
        return re.match(r'\.+\w*', imp).group()
    return re.match(r'\w+', imp).group()


def get_paths(module, local_list):
    module = strip_to_first_module(module)
    if not module:
        raise Exception('No module')

    if module[0] == '.':
        return RELATIVE

    if module == '__future__':
        return FUTURE

    if module in local_list:
        return LOCAL

    if module in STDLIB_NAMES:
        return STDLIB

    return THIRDPARTY
