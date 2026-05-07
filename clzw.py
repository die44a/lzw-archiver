#!/usr/bin/env python3
"""Console version of LZW archiver"""


from logic.packer import TarPacker
from pathlib import Path
import tempfile
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

    parser.add_argument(
        'PATH', type=str,
        help='path to the file or directory to compress/extract')

    parser.add_argument(
        '-o', '--output', type=str,
        metavar='OUTPUT',
        help='path to the output directory after extraction')

    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='rewrite existing output directory if exists')

    return parser.parse_args()


def main():
    args = parse_args()

    packer = TarPacker()
    archiver = LZWArchiver()

    input_path = Path(args.PATH)

    tmp_path = None
    try:
        if args.compress:
            output = input_path.with_name(input_path.name + '.lzw')

            tmp = tempfile.NamedTemporaryFile(mode='w', delete=False)
            tmp_path = Path(tmp.name)
            tmp.close()

            packed = packer.pack(input_path, tmp_path)
            archiver.encode(packed, output)

        elif args.extract:
            if args.output:
                output = Path(args.output).resolve()
            else:
                clean_name = input_path.name.split('.')[0]
                output = input_path.parent / clean_name

            tmp = tempfile.NamedTemporaryFile(mode='r', delete=False)
            tmp_path = Path(tmp.name)
            tmp.close()

            archiver.decode(input_path, tmp_path)
            unpacked = packer.unpack(tmp_path, output)

    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()


if __name__ == "__main__":
    main()
