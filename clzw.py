#!/usr/bin/env python3

"""Console version of LZW archiver"""


import re
import os
import logging
import inspect
import enum
import argparse
import sys


ERROR_EXCEPTION = 1
ERROR_PYTHON_VERSION = 2
ERROR_MODULES_MISSING = 3

if sys.version_info < (3, 10):
    print('Use python >= 3.10', file=sys.stderr)
    sys.exit(ERROR_PYTHON_VERSION)

try:
    import readline
except ImportError:
    pass

try:
    from logic import LZWArchiver
except Exception as e:
    print('Archives modeles were not found: "{}"'.format(e), file=sys.stderr)
    sys.exit(ERROR_MODULES_MISSING)

__version__ = '0.1'
__author__ = 'Dima Borisov'
__email__ = 'dim4ig2007@gmail.com'


def parse_args():
    """Command line arguments parsing"""
    parser = argparse.ArgumentParser(
        prog='LZW-Archiver',
        description=f'Compresses or extracts files from specified file or directory',
        epilog=f'Author: {__author__} <{__email__}>')

    group = parser.add_mutually_exclusive_group(required=True)

    parser.add_argument(
        '-V', '--version',
        action='version',
        version=f'%(prog)s {__version__}')

    group.add_argument(
        '-x', '--extract',
        action='store_true',
        help='extract file or directory')

    group.add_argument(
        '-c', '--compress',
        action='store_true',
        help='compress file or directory')

    parser.add_argument('PATH', type=str,
                        help='path to the file or directory')

    parser.add_argument(
        '-o', '--output', type=str,
        metavar='OUTPUT',
        help='path to the output directory')

    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='rewrite existing output directory if exists')

    return parser.parse_args()


def main():
    pass


if __name__ == "__main__":
    main()
