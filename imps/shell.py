from __future__ import absolute_import, division, print_function

import argparse
import os

from core import Sorter, Style


def get_style(s):
    if s in ('s', 'smarkets'):
        return Style.SMARKETS
    elif s in ('g', 'google'):
        return Style.GOOGLE
    elif s in ('c', 'cryptography'):
        return Style.CRYPTOGRAPHY
    else:
        raise Exception('Unknown style type %s', s)


def run(sorter, file_name):
    data = ''
    for line in file(file_name):
        data += line

    print(sorter.sort(data))


def recurse_down_tree(sorter, path):
    for subdir, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(subdir, file)
            if file_path[-3:] == '.py':
                run(sorter, file_path)


def get_args():
    parser = argparse.ArgumentParser(description='Sort your python')

    parser.add_argument('-s', '--style', type=str, help='Import style', default='s')
    parser.add_argument('-f', '--file_name', help='File to sort', type=str, default=None)
    parser.add_argument('-p', '--path', help='Path to sort', type=str, default='.')

    args = parser.parse_args()

    sorter = Sorter(get_style(args.style))

    if args.file_name:
        run(sorter, args.file_name)
    else:
        recurse_down_tree(sorter, args.path)


get_args()
