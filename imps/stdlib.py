from __future__ import absolute_import, division, print_function

from importlib import import_module

from flake8_import_order import STDLIB_NAMES


FUTURE = 0
STDLIB = 1
THIRDPARTY = 2
LOCAL = 3
RELATIVE = -1

#
# from glob import glob
# from sys import path as PYTHONPATH
#
#
#
# # lifted from isort/isort.py
# def get_paths2(module_name):
#     if module_name == '__future__':
#         return FUTURE
#
#     paths = PYTHONPATH
#     virtual_env = os.environ.get('VIRTUAL_ENV')  # self.config.get('virtual_env')
#     virtual_env_src = False
#
#     if virtual_env:
#         paths += [path for path in glob('{0}/lib/python*/site-packages'.format(virtual_env))
#                   if path not in paths]
#         paths += [path for path in glob('{0}/src/*'.format(virtual_env)) if os.path.isdir(path)]
#         virtual_env_src = '{0}/src/'.format(virtual_env)
#
#     for prefix in paths:
#         module_path = "/".join((prefix, module_name.replace(".", "/")))
#         package_path = "/".join((prefix, module_name.split(".")[0]))
#         if (os.path.exists(module_path + ".py") or os.path.exists(module_path + ".so") or
#            (os.path.exists(package_path) and os.path.isdir(package_path))):
#             if ('site-packages' in prefix or 'dist-packages' in prefix
#                     or (virtual_env and virtual_env_src in prefix)):
#                 return THIRDPARTY
#             elif 'python2' in prefix.lower() or 'python3' in prefix.lower():
#                 return STDLIB
#             else:
#                 return LOCAL
#     return LOCAL


def get_paths(module, local_list):
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


def get_paths_old(module):
    if module and module[0] == '.':
        return RELATIVE

    if module == '__future__':
        return FUTURE

    # Stop system from unloading itself
    if module == 'imps':
        return LOCAL

    if module in STDLIB_NAMES:
        return STDLIB

    try:
        m = import_module(module)
    except ImportError:
        return LOCAL
    else:
        file_path = m.__file__
        if 'site-packages' in file_path or 'dist-packages' in file_path:
            return THIRDPARTY
        elif 'python2' in file_path or 'python3' in file_path:
            return STDLIB
        else:
            return LOCAL
