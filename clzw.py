#!/usr/bin/env python3
"""Console version of LZW archiver"""


import shutil

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


def split_name(path: Path):
    suffixes = ''.join(path.suffixes)
    root = path.name[:-len(suffixes)] if suffixes else path.name
    return root, suffixes


def next_free(path: Path) -> Path:
    if not path.exists():
        return path
    root, suffixes = split_name(path)
    i = 1
    while True:
        candidate = path.with_name(f"{root}({i}){suffixes}")
        if not candidate.exists():
            return candidate
        i += 1


def collect_targets(path: Path):
    if path.is_file():
        return [path]

    result = []

    for item in path.iterdir():
        if item.is_file():
            result.append(item)
        if item.is_dir():
            result.extend(collect_targets(item))
    return result


def show_targets(targets):
    print('These files/directories will be affected:\n')
    for t in targets:
        print(" -", t)


def confirm():
    answer = input('\nProceed? (y/n): ').strip().lower()
    return answer in ('y', 'yes')


def clear(path: Path):
    if not path.exists():
        return

    if path.is_file() or path.is_symlink():
        path.unlink()
    if not path.exists():
        return

    shutil.rmtree(path, ignore_errors=True)


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
        help='overwrite existing files and directories without prompting')

    return parser.parse_args()


def main():
    "Program entry point"
    args = parse_args()

    packer = TarPacker()
    archiver = LZWArchiver()

    input_path = Path(args.PATH)

    tmp_path = None
    try:  # Using 'try' construction to delete tmp file at the end
        if args.compress:
            output = Path(args.output) if args.output else next_free(
                input_path.with_name(input_path.name + '.lzw'))

            if output.exists() and not args.force:
                print('Error:')
                print(f'Output file/directory already exists: {output}')
                print(f'Warning: continuing will overwrite its contents')
                if not confirm():
                    print('Compressing aborted')
                    return

            tmp = tempfile.NamedTemporaryFile(delete=False)
            tmp_path = Path(tmp.name)
            tmp.close()

            packed = packer.pack(input_path, tmp_path)
            archiver.encode(packed, output)

            print(f'{input_path.name} was succesfully compressed to {output.name}')

        elif args.extract:
            output = Path(args.output or split_name(input_path)[0]).resolve()

            if output.exists():
                if not args.force:
                    print('Error:')
                    print(f'Output file/directory already exists: {output}')
                    print(f'Warning: continuing will overwrite its contents')
                    affected = collect_targets(output)
                    show_targets(affected)
                    if not confirm():
                        print('Extracting aborted')
                        return

                clear(output)

            output.mkdir(parents=True, exist_ok=True)

            tmp = tempfile.NamedTemporaryFile(delete=False)
            tmp_path = Path(tmp.name)
            tmp.close()

            archiver.decode(input_path, tmp_path)
            unpacked = packer.unpack(tmp_path, output)

            print(
                f'{input_path.name} was succesfully extracted to the directory {output}')

    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()


if __name__ == "__main__":
    main()
