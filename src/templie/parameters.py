"""
Global parameters
"""

from re import search

from .utils import remove_backslashes
from .exceptions import DslSyntaxError
from .constants import IDENTIFIER_REGEX


def parameters(lines):
    pairs = (__get_key_value_pair(line) for line in lines)
    return {name: value for name, value in pairs}


def __get_key_value_pair(line):
    match = search(r'^\s*({})\s*=\s*(?:([^" ]+)|"((?:\\.|[^"])*)")\s*$'.format(IDENTIFIER_REGEX), line)
    if match:
        name, value, quoted_value = match.groups()
        return name, value if value else remove_backslashes(quoted_value)
    raise DslSyntaxError.get_error(line)