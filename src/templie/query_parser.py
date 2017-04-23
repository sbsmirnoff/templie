"""
Parser
"""

from re import search

from templie.exceptions import ParseException
from templie.sections import IDENTIFIER_REGEX


def parse_join(line):
    identifiers = [IDENTIFIER_REGEX] * 5
    match = search(r'^\s*join\s+({})\s+on\s+({}\.{})\s*=\s*({}\.{})\s*(.*)$'.format(*identifiers), line)
    if match:
        table, left_column, right_column, rest = match.groups()
        parsed = [(table, left_column, right_column)]
        return parsed + parse_join(rest) if rest else parsed
    raise ParseException


def parse(line):
    match = search(r'^\s*({})\s*(.*)$'.format(IDENTIFIER_REGEX), line)
    if match:
        table, rest = match.groups()
        joins = parse_join(rest) if rest else []
        return table, joins
    raise ParseException


if __name__ == '__main__':
    ttt = parse('aaa') # join bbb on bbb.x  = aaa.y join ccc on ccc.rr = aaa._hdhd_ii')
    print(ttt)
