from __future__ import absolute_import, division, print_function

import argparse
import difflib
import os
import sys

from backports import configparser

from imps.core import Sorter


def run(sorter, file_name, is_dry_run):
    # Why not send array of lines in if that's what we use?
    with open(file_name, 'r') as f:
        data = f.read()

    output = sorter.sort(data)
    if output:
        if is_dry_run:
            result = difflib.unified_diff(output.splitlines(), data.splitlines())
            print('\n'.join(result))
        else:
            with open(file_name, 'w') as f:
                f.write(output)


def recurse_down_tree(args, path, sorter=None):
    is_dry_run = args.dry_run
    if os.path.isfile(path):
        run(get_sorter(args, path), path, is_dry_run)
    else:
        files = os.listdir(path)
        if 'setup.cfg' in files or sorter is None:
            sorter = get_sorter(args, path)
        for f in files:
            if os.path.isfile(os.path.join(path, f)) and f[-3:] == '.py':
                run(sorter, os.path.join(path, f), is_dry_run)
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


def normalize_file_name(file_name):
    orig_file_name = file_name

    while not os.path.exists(file_name) and ':' in file_name:
        file_name = file_name[0:file_name.rfind(':')]

    if os.path.exists(file_name):
        return file_name

    print('File %s does not exist' % orig_file_name, file=sys.stderr)
    return None


def normalize_file_names(file_list):
    return [normalize_file_name(f) for f in file_list if normalize_file_name(f)]


def setup_vars(config, args):
    # Read from command line first. Else setup.cfg 'imps' else 'flake8'. Else assume 's'
    style = args.style
    if not style:
        style = config.get('imps', 'style', fallback=config.get('flake8', 'import-order-style', fallback='s'))

    max_line_length = args.max_line_length
    if not max_line_length:
        max_line_length = config.get('imps', 'max-line-length', fallback=config.get(
            'flake8', 'max-line-length', fallback=80
        ))

    application_import_names = args.application_import_names
    if not application_import_names:
        application_import_names = config.get(
            'imps', 'application-import-names', fallback=config.get(
                'flake8', 'application-import-names', fallback=''
            )
        )

    return style, max_line_length, application_import_names.split(',')


def main():
    parser = argparse.ArgumentParser(description='Sort your python')

    parser.add_argument('file', nargs='*', default=[os.getcwd()])

    parser.add_argument('-s', '--style', type=str, help='Import style', default='')
    parser.add_argument('-l', '--max-line-length', type=int, help='Line length')
    parser.add_argument('-n', '--application-import-names', type=str, help='Local Imports')

    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true')
    parser.set_defaults(dry_run=False)

    args = parser.parse_args()
    file_names = normalize_file_names(args.file)
    for file_name in file_names:
        recurse_down_tree(args, file_name)


if __name__ == "__main__":
    main()
