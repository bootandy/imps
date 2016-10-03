from __future__ import absolute_import, division,  print_function
import operator
import os
import sys
from contextlib import contextmanager
from importlib import import_module

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


def get_paths(module):
    if module and module[0] == '.':
        return RELATIVE

    if module == '__future__':
        return FUTURE

    # Stop system from unloading itself
    if module == 'imps':
        return LOCAL

    # sys has no file
    if module in ('sys', 'operator'):
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


@contextmanager
def ignore_site_packages_paths():
    paths = sys.path[:]
    # remove working directory so that all
    # local imports fail
    if os.getcwd() in sys.path:
        sys.path.remove(os.getcwd())
    # remove all third-party paths
    # so that only stdlib imports will succeed
    sys.path = list(set(filter(
        None,
        filter(lambda i: all(('site-packages' not in i, 'python' in i or 'pypy' in i)),
               map(operator.methodcaller('lower'), sys.path))
    )))
    yield
    sys.path = paths


def get_paths3(module):
    if module[0] == '.':
        return RELATIVE

    if module == '__future__':
        return FUTURE

    # Stop system from unloading itself
    if module == 'imps':
        return LOCAL

    if module == 'pytest':
        return THIRDPARTY

    if module == 'os':  # tests break without this
        return STDLIB

    with ignore_site_packages_paths():
        imported_module = sys.modules.pop(module, None)
        try:
            import_module(module)
        except ImportError:
            pass
        else:
            return STDLIB
        finally:
            if imported_module:
                sys.modules[module] = imported_module

    imported_module = sys.modules.pop(module, None)
    try:
        import_module(module)
    except ImportError:
        return LOCAL
    else:
        return THIRDPARTY
    finally:
        if imported_module:
            sys.modules[module] = imported_module


# print(get_paths('pytest'))
# print(get_paths('os'))
# print(get_paths('sys'))
# print(get_paths('nothing'))
# print(get_paths('imps'))
# print(get_paths('_io'))
