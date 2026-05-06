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
