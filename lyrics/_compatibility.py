"""
This is a compatibility module, to make it possible to use lyrics also with
older python versions.
"""

import sys

is_py3k = sys.version_info >= (3,)

# unicode function
try:
    unicode = unicode
except NameError:
    unicode = str
