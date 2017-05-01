"""
Parser
"""

from re import search, split
from itertools import groupby

from .exceptions import ParseException
from .constants import IDENTIFIER_REGEX
from .query import Query


def parse_join(line):
    identifiers = [IDENTIFIER_REGEX] * 9
    match = search(
        r'^\s*join\s+({})\s+on\s+({}\.{}(?:,{}\.{})*)\s*=\s*({}\.{}(?:,{}\.{})*)\s*(.*)$'.format(*identifiers),
        line
    )
    if match:
        table, left_column, right_column, rest = match.groups()
        parsed = [Join(table, left_column, right_column)]
        return parsed + parse_join(rest) if rest else parsed
    raise ParseException


def parse_column_tuple(columns):
    return split(r'\s*,\s*', columns)


def parse(line):
    match = search(r'^\s*({})\s*(.*)$'.format(IDENTIFIER_REGEX), line)
    if match:
        table, rest = match.groups()
        joins = parse_join(rest) if rest else []
        return table, joins
    raise ParseException


class Join:

    def __init__(self, table, left_columns, right_columns):
        if len(left_columns) != len(right_columns):
            raise ParseException
        self.table = table
        self.left_columns = []
        self.right_columns = []
        for left, right in zip(left_columns, right_columns):
            left_table, left_column = left.split('.')
            right_table, right_column = right.split('.')
            if left_table == table and right_table != table:
                self.left_columns.append(right_column)
                self.right_columns.append(left_column)
            elif left_table != table and right_table == table:
                self.left_columns.append(left_column)
                self.right_columns.append(right_column)
            else:
                raise ParseException


def dict_providers(join):

    def provider(columns):
        return lambda table: tuple(table[column] for column in columns)

    return provider(join.left_columns), provider(join.right_columns)


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
