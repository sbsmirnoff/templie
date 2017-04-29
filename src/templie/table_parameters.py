"""
CSV Parameters class
"""

from re import search, split

from .utils import lines_to_csv, has_duplicates, remove_backslashes, grouped
from .exceptions import DslSyntaxError, ValidationError
from .constants import IDENTIFIER_REGEX


class TableParameters:

    def __init__(self, lines):
        self.__validate_lines(lines)
        flat = self.__is_flat_indicator(lines[0])
        header, *body = lines[1:] if flat else lines
        self.__number_of_columns = len(split(r'\s*,\s*|\s*;\s*|\s+', header))
        self.__lines = lines_to_csv(body, self.__number_of_columns) if flat else body
        self.__names = self.__parse_names(header)
        self.__values_pattern = self.__compound_regex(r'\s*(?:([^,;" ]+)|"((?:\\.|[^"])*)")\s*')

    def __iter__(self):
        for line in self.__lines:
            yield self.__name_value_map(line)

    @staticmethod
    def __validate_lines(lines):
        if not lines or (TableParameters.__is_flat_indicator(lines[0]) and len(lines) < 2):
            raise ValidationError.get_error('One of repeater parameter sections is empty')

    def __compound_regex(self, unit_regex):
        parts = [unit_regex] * self.__number_of_columns
        regex = r'[,; ]'.join(parts)
        return r'^{}$'.format(regex)

    def __parse_names(self, line):
        pattern = self.__compound_regex(r'\s*({})\s*'.format(IDENTIFIER_REGEX))
        match = search(pattern, line)
        if not match:
            raise DslSyntaxError.get_error(line)
        names = match.groups()
        if has_duplicates(names):
            raise ValidationError.get_error('Name conflicts in repeater parameter section')
        return names

    def __parse_values(self, line):
        match = search(self.__values_pattern, line)
        if match:
            return [
                value if value else remove_backslashes(quoted_value)
                for value, quoted_value in grouped(match.groups(), 2)
            ]
        raise DslSyntaxError.get_error(line)

    def __name_value_map(self, line):
        return {
            name: value
            for name, value in zip(self.__names, self.__parse_values(line))
        }

    @staticmethod
    def __is_flat_indicator(line):
        return bool(search(r'^\s*\*flat\*\s*$', line))
