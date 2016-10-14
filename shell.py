from __future__ import absolute_import, division, print_function

import argparse
import os

import configparser

from imps.core import Sorter, Style


def get_style(s):
    if s in ('s', 'smarkets'):
        return Style.SMARKETS
    elif s in ('g', 'google'):
        return Style.GOOGLE
    elif s in ('c', 'crypto', 'cryptography'):
        return Style.CRYPTOGRAPHY
    else:
        raise Exception('Unknown style type %s', s)


def run(sorter, file_name):
    data = ''
    for line in file(file_name):
        data += line

    output = sorter.sort(data)
    if output:
        with open(file_name, 'w') as f:
            f.write(output)


def recurse_down_tree(sorter, path):
    if path[-3:] == '.py':
        run(sorter, path)
    else:
        for subdir, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(subdir, file)
                if file_path[-3:] == '.py':
                    run(sorter, file_path)


def get_config(path):
    if os.path.isfile(path):
        path, _ = os.path.split(path)

    config = configparser.ConfigParser()

    # handle no config file ever found
    while not config.sections():
        config.read(os.path.join(path, 'setup.cfg'))
        path = os.path.join(path, '..')

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

    return style, max_line_length



def get_args():
    parser = argparse.ArgumentParser(description='Sort your python')

    parser.add_argument('file', nargs='?', default=os.getcwd())

    parser.add_argument('-s', '--style', type=str, help='Import style', default='')
    parser.add_argument('-l', '--max-line-length', type=int, help='Line length')

    args = parser.parse_args()

    config = get_config(args.file)
    style, max_line_length = setup_vars(config, args)

    sorter = Sorter(get_style(style))

    recurse_down_tree(sorter, args.file)


get_args()
