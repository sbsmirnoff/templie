"""
Template class
"""

from re import finditer, search
import string

from .exceptions import ValidationError
from .constants import COMPOUND_IDENTIFIER_REGEX


class _StringTemplate(string.Template):
    idpattern = COMPOUND_IDENTIFIER_REGEX


class Template:

    def __init__(self, lines, name):
        self.__content = ''.join(lines)
        self.__name = name
        self.__string_template = _StringTemplate(self.__content)

    @property
    def names(self):
        return {
            match.group(1) if match.group(1) else match.group(2)
            for match
            in finditer(r'\$(?:(%s)|{(%s)})' % (COMPOUND_IDENTIFIER_REGEX, COMPOUND_IDENTIFIER_REGEX), self.__content)
        }

    def generate(self, params):
        return self.__string_template.substitute(params)

    def validate(self):
        match = search(r'\$\s', self.__content)
        if match:
            msg = "{} contains a standalone delimiter '$'. Use '$$' if you want a dollar sign in your template"
            raise ValidationError.get_error(msg.format(self.__name))
