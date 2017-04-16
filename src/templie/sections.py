"""
Section classes and functions
"""

from re import search
from re import split
from re import finditer
from string import Template as StringTemplate

from .utils import grouped, clean_up_lines, lines_to_csv
from .exceptions import DslSyntaxError, ValidationError

IDENTIFIER_REGEX = r'[_a-zA-Z][_a-zA-Z0-9]*'


class Template:

    def __init__(self, content, name):
        self.__content = content
        self.__name = name
        self.__string_template = StringTemplate(content)

    def get_names(self):
        matches = [
            match.group(1) if match.group(1) else match.group(2)
            for match in finditer(r'\$(?:(%s)|{(%s)})' % (IDENTIFIER_REGEX, IDENTIFIER_REGEX), self.__content)
        ]
        return iter(matches)

    def generate(self, params):
        return self.__string_template.substitute(params)

    def validate(self):
        match = search(r'\$\s', self.__content)
        if match:
            msg = "{} contains a standalone delimiter '$'. Use '$$' if you want a dollar sign in your template"
            raise ValidationError.get_error(msg.format(self.__name))


class RepeaterParameters:

    def __init__(self, lines, flat):
        cleaned_lines = list(clean_up_lines(lines))
        header, body = cleaned_lines[0], cleaned_lines[1:]
        self.__number_of_columns = len(split(r'\s*,\s*|\s*;\s*|\s+', header))
        self.__lines = lines_to_csv(body, self.__number_of_columns) if flat else body
        self.__names = self.__parse_names(header)

    def __iter__(self):
        for line in self.__lines:
            yield self.__name_value_map(line)

    def get_names(self):
        return self.__names

    def __compound_regex(self, unit_regex):
        parts = [unit_regex] * self.__number_of_columns
        regex = r'[,; ]'.join(parts)
        return r'^{}$'.format(regex)

    def __parse_names(self, line):
        pattern = self.__compound_regex(r'\s*({})\s*'.format(IDENTIFIER_REGEX))
        match = search(pattern, line)
        if match:
            return match.groups()
        raise DslSyntaxError.get_error(line)

    def __parse_values(self, line):
        pattern = self.__compound_regex(r'\s*(?:([^,;" ]+)|"([^"]*)")\s*')
        match = search(pattern, line)
        if match:
            return [
                value if value else quoted_value
                for value, quoted_value in grouped(match.groups(), 2)
            ]
        raise DslSyntaxError.get_error(line)

    def __name_value_map(self, line):
        return {
            name: value
            for name, value in zip(self.__names, self.__parse_values(line))
        }


def parameters(lines):
    pairs = (__get_key_value_pair(line) for line in clean_up_lines(lines))
    return {name: value for name, value in pairs}


def __get_key_value_pair(line):
    match = search(r'^\s*({})\s*=\s*(?:([^" ]+)|"([^"]*)")\s*$'.format(IDENTIFIER_REGEX), line)
    if match:
        name, value, quoted_value = match.groups()
        return name, value if value else quoted_value
    raise DslSyntaxError.get_error(line)
