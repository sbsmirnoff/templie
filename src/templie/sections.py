"""
Section classes and functions
"""

from re import finditer
from re import search
from re import split
from string import Template as StringTemplate

from .exceptions import DslSyntaxError, ValidationError, MissingSection, WrongValue
from .utils import grouped, clean_up_lines, lines_to_csv, has_duplicates, remove_backslashes

IDENTIFIER_REGEX = r'[_a-zA-Z][_a-zA-Z0-9]*'
CONFIG_SECTION = 'CONFIG'
TEMPLATE = 'template'
GLOBAL_PARAMETERS = 'global_parameters'
REPEATER_PARAMETERS = 'repeater_parameters'
FLAT_REPEATER = 'flat_repeater'


class Template:

    def __init__(self, lines, name):
        self.__content = ''.join(lines)
        self.__name = name
        self.__string_template = StringTemplate(self.__content)

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
        header, *body = lines
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
        pattern = self.__compound_regex(r'\s*(?:([^,;" ]+)|"((?:\\.|[^"])*)")\s*')
        match = search(pattern, line)
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


def parameters(lines):
    pairs = (__get_key_value_pair(line) for line in lines)
    return {name: value for name, value in pairs}


def __get_key_value_pair(line):
    match = search(r'^\s*({})\s*=\s*(?:([^" ]+)|"((?:\\.|[^"])*)")\s*$'.format(IDENTIFIER_REGEX), line)
    if match:
        name, value, quoted_value = match.groups()
        return name, value if value else remove_backslashes(quoted_value)
    raise DslSyntaxError.get_error(line)


class Sections:

    def __init__(self, section_lines, config_parameters):
        self.__template_name = config_parameters[TEMPLATE]
        self.__global_parameters_name = config_parameters[GLOBAL_PARAMETERS]
        self.__repeater_parameters_name = config_parameters[REPEATER_PARAMETERS]
        self.__flat = self.__is_flat_repeater(config_parameters)
        self.__section_lines = section_lines
        self.__set_sections()

    def __set_sections(self):
        self.template = self.__get_template()
        self.global_parameters = self.__get_global_parameters_section()
        self.repeater_parameters = self.__get_repeater_parameters_section()

    def __get_template(self):
        lines = self.__section_lines.get(self.__template_name)
        if lines:
            return Template(lines, self.__template_name)
        raise MissingSection.get_error(self.__template_name)

    def __get_global_parameters_section(self):
        lines = self.__section_lines.get(self.__global_parameters_name)
        if lines:
            return parameters(clean_up_lines(lines))
        raise MissingSection.get_error(self.__global_parameters_name)

    def __get_repeater_parameters_section(self):
        lines = self.__section_lines.get(self.__repeater_parameters_name)
        if lines:
            return RepeaterParameters(clean_up_lines(lines), self.__flat)
        raise MissingSection.get_error(self.__repeater_parameters_name)

    @staticmethod
    def __is_flat_repeater(config_parameters):
        flat = config_parameters.get(FLAT_REPEATER, 'false')
        if flat == 'false':
            return False
        elif flat == 'true':
            return True
        else:
            raise WrongValue.get_error(FLAT_REPEATER, 'either "true" or "false"')

    def validate(self):
        self.template.validate()

        if has_duplicates(self.repeater_parameters.get_names()):
            raise ValidationError.get_error('Name conflicts in repeater parameter section')

        global_parameters_names = set(self.global_parameters.keys())
        repeater_parameters_names = set(self.repeater_parameters.get_names())

        if global_parameters_names & repeater_parameters_names:
            raise ValidationError.get_error('Name conflicts in global and repeater parameter sections')

        template_variables = set(self.template.get_names())
        undefined_template_variables = template_variables - (global_parameters_names | repeater_parameters_names)
        if undefined_template_variables:
            raise ValidationError.get_error(
                'Undefined variables in the template: {}'.format(', '.join(undefined_template_variables))
            )
