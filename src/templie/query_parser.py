"""
Parser
"""

from re import search

from templie.exceptions import ParseException
from templie.sections import IDENTIFIER_REGEX


def parse_from(line):
    match = search(r'^\s*from\s+({})\s*(.*)$'.format(IDENTIFIER_REGEX), line)
    return match.groups() if match else ()


def parse_join(line):
    identifiers = [IDENTIFIER_REGEX] * 5
    match = search(r'^\s*join\s+({})\s+on\s+({}\.{})\s*=\s*({}\.{})\s*(.*)$'.format(*identifiers), line)
    if match:
        table, left_column, right_column, rest = match.groups()
        parsed = [(table, left_column, right_column)]
        return parsed + parse_join(rest) if rest else parsed
    raise ParseException


def parse(line):
    parsed = parse_from(line)
    if parsed:
        return parsed[0], parse_join(parsed[1])


if __name__ == '__main__':
    ttt = parse('from aaa join bbb on aaa.x  = bbb.y join ccc on bbb.rr = ccc._hdhd_ii')
    print(ttt)
