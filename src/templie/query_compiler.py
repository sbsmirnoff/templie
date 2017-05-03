"""
Parser
"""

from re import search, split
from itertools import groupby

from .exceptions import ParseException, DslSyntaxError
from .constants import IDENTIFIER_REGEX
from .query import Query


def _parse_join(line):
    identifiers = [IDENTIFIER_REGEX] * 9
    match = search(
        r'^\s*join\s+({})\s+on\s+({}\.{}(?:\s*,\s*{}\.{})*)\s*=\s*({}\.{}(?:\s*,\s*{}\.{})*)\s*(.*)$'.format(*identifiers),
        line
    )
    if match:
        table, left_columns, right_columns, rest = match.groups()
        parsed = [_Join(table, _parse_column_tuple(left_columns), _parse_column_tuple(right_columns))]
        return parsed + _parse_join(rest) if rest else parsed
    raise ParseException


def _parse_column_tuple(columns):
    return split(r'\s*,\s*', columns)


def parse(line):
    match = search(r'^\s*({})\s*(.*)$'.format(IDENTIFIER_REGEX), line)
    if match:
        table, rest = match.groups()
        joins = _parse_join(rest) if rest else []
        return table, joins
    raise ParseException


class _Join:

    def __init__(self, table, left_columns, right_columns):
        if len(left_columns) != len(right_columns):
            raise ParseException
        self.table = table
        self.left_columns = []
        self.right_columns = []
        self.joined_tables = []
        for left, right in zip(left_columns, right_columns):
            left_table, left_column = left.split('.')
            right_table, right_column = right.split('.')
            if left_table == table and right_table != table:
                self.left_columns.append(right_column)
                self.right_columns.append(left_column)
                self.joined_tables.append(right_table)
            elif left_table != table and right_table == table:
                self.left_columns.append(left_column)
                self.right_columns.append(right_column)
                self.joined_tables.append(left_table)
            else:
                raise ParseException


def dict_providers(join):

    def left_provider(columns):
        return lambda tables: tuple(table[column] for table, column in zip(tables, columns))

    def right_provider(columns):
        return lambda table: tuple(table[column] for column in columns)

    return left_provider(join.left_columns), right_provider(join.right_columns)


def _group_name_value_pairs(pairs):
    def key(pair):
        return pair[0].split('.')[1]
    pairs.sort(key=key)
    return groupby(pairs, key=key)


def dict_row_constructor(row):
    pairs = [
        ('{}.{}'.format(table, column_name), value)
        for table, columns in row.items()
        for column_name, value in columns.items()
    ]
    grouped = _group_name_value_pairs(pairs)
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
            query = join_clause.on(join.joined_tables, self.providers_factory(join))
        return query.select(self.row_factory)


def create_query(line):
    try:
        return CompiledQuery(line, dict_providers, dict_row_constructor)
    except ParseException:
        raise DslSyntaxError.get_error(line)
