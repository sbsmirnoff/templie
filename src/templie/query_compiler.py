"""
Parser
"""

from re import search
from itertools import groupby

from .exceptions import ParseException
from .constants import IDENTIFIER_REGEX
from .query import Query


def parse_join(line):
    identifiers = [IDENTIFIER_REGEX] * 5
    match = search(r'^\s*join\s+({})\s+on\s+({}\.{})\s*=\s*({}\.{})\s*(.*)$'.format(*identifiers), line)
    if match:
        table, left_column, right_column, rest = match.groups()
        parsed = [Join(table, left_column, right_column)]
        return parsed + parse_join(rest) if rest else parsed
    raise ParseException


def parse(line):
    match = search(r'^\s*({})\s*(.*)$'.format(IDENTIFIER_REGEX), line)
    if match:
        table, rest = match.groups()
        joins = parse_join(rest) if rest else []
        return table, joins
    raise ParseException


class Join:

    def __init__(self, table, left_column, right_column):
        self.table = table
        left_table, self.left_column = left_column.split('.')
        right_table, self.right_column = right_column.split('.')
        if left_table == table and right_table != table:
            self.joined_table = right_table
            self.joined_table_on_left = False
        elif left_table != table and right_table == table:
            self.joined_table = left_table
            self.joined_table_on_left = True
        else:
            raise ParseException


def dict_providers(join):

    def left_provider(table):
        return table[join.left_column if join.joined_table_on_left else join.right_column]

    def right_provider(table):
        return table[join.right_column if join.joined_table_on_left else join.left_column]

    return left_provider, right_provider


def dict_row_constructor(row):
    pairs = [
        ('%s.%s' % (table, column_name), value)
        for table, columns in row.items()
        for column_name, value in columns.items()
    ]

    def key(pair):
        return pair[0].split('.')[1]
    pairs.sort(key=key)
    grouped = groupby(pairs, key=key)

    result = {}
    for key, values in grouped:
        values = list(values)
        if len(values) == 1:
            result[key] = values[0][1]
            result[values[0][0]] = values[0][1]
        else:
            result.update(dict(values))
    return result


class CompiledQuery:

    def __init__(self, line, providers_factory, row_factory):
        self.table, self.joins = parse(line)
        self.providers_factory = providers_factory
        self.row_factory = row_factory

    @property
    def names(self):
        return [self.table] + [join.table for join in self.joins]

    def query(self, collections):
        first, *rest = collections
        query = Query(name=self.table, iterable=first)
        for join, collection in zip(self.joins, rest):
            join_clause = query.equi_join(join.table, collection)
            query = join_clause.on(join.joined_table, self.providers_factory(join))
        return query.select(self.row_factory)


def create_query(line):
    return CompiledQuery(line, dict_providers, dict_row_constructor)
