from __future__ import absolute_import, division, print_function

import argparse
import os

from backports import configparser

from imps.core import Sorter


def run(sorter, file_name):
    # Why not send array of lines in if that's what we use?
    data = file(file_name).read()

    output = sorter.sort(data)
    if output:
        with open(file_name, 'w') as f:
            f.write(output)


def recurse_down_tree(args, path, sorter=None):
    if os.path.isfile(path):
        run(get_sorter(args, path), path)
    else:
        files = os.listdir(path)
        if 'setup.cfg' in files or sorter is None:
            sorter = get_sorter(args, path)
        for f in files:
            if os.path.isfile(os.path.join(path, f)) and f[-3:] == '.py':
                run(sorter, os.path.join(path, f))
            elif not os.path.isfile(f) and '.' not in f:
                recurse_down_tree(args, os.path.join(path, f), sorter)


def get_sorter(args, path):
    if os.path.isfile(path):
        path, _ = os.path.split(path)
    conf = read_config(os.path.abspath(path))
    style, max_line_length, local_imports = setup_vars(conf, args)
    return Sorter(style, max_line_length, local_imports)


def read_config(path):
    config = configparser.ConfigParser()
    while not config.sections() and path != '/':
        config.read(os.path.join(path, 'setup.cfg'))
        path, _ = os.path.split(path)
    return config


def setup_vars(config, args):
    # Read from command line first. Else setup.cfg 'imps' else 'flake8'. Else assume 's'
    style = args.style
    if not style:
        style = config.get('imps', 'style', fallback=None)
    if not style:
        style = config.get('flake8', 'import-order-style', fallback=None)
    if not style:
        style = 's'

    max_line_length = args.max_line_length
    if not max_line_length:
        max_line_length = config.get('imps', 'max-line-length', fallback=None)
    if not max_line_length:
        max_line_length = config.get('flake8', 'max-line-length', fallback=None)
    if not max_line_length:
        max_line_length = 80

    # These all look similar can we remove some code dup?
    application_import_names = args.application_import_names
    if not application_import_names:
        application_import_names = config.get('imps', 'application-import-names', fallback='')
    if not application_import_names:
        application_import_names = config.get('flake8', 'application-import-names', fallback='')

    return style, max_line_length, application_import_names.split(',')


def main():
    parser = argparse.ArgumentParser(description='Sort your python')

    parser.add_argument('file', nargs='?', default=os.getcwd())

    parser.add_argument('-s', '--style', type=str, help='Import style', default='')
    parser.add_argument('-l', '--max-line-length', type=int, help='Line length')
    parser.add_argument('-n', '--application-import-names', type=str, help='Local Imports')

    args = parser.parse_args()

    recurse_down_tree(args, args.file)


if __name__ == "__main__":
    main()
