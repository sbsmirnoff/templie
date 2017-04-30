"""
Sections class
"""

from re import split

from .exceptions import ValidationError, MissingSection, MissingParameter
from .query_compiler import create_query
from .template import Template
from .table_parameters import TableParameters
from .parameters import parameters
from .utils import clean_up_lines

TEMPLATE = 'template'
GLOBAL_PARAMETERS = 'global_parameters'
REPEATER_PARAMETERS = 'repeater_parameters'
FLAT_REPEATER = 'flat_repeater'


class Sections:

    def __init__(self, section_lines, config_section):
        self.__section_lines = section_lines
        self.__config_section = config_section
        config_parameters = self.__get_config_parameters()
        self.__template_name = config_parameters[TEMPLATE]
        self.__global_parameters_name = config_parameters[GLOBAL_PARAMETERS]
        self.__repeater_parameters_name = config_parameters[REPEATER_PARAMETERS]

        self.__template = self.__get_template()
        self.__global_parameters = self.__get_global_parameters_section()
        self.__repeater_parameters = self.__get_repeater_parameters_section()

    def nonempty(self):
        return bool(self.__repeater_parameters)

    def __get_template(self):
        lines = self.__section_lines.get(self.__template_name)
        if lines:
            return Template(lines, self.__template_name)
        raise MissingSection.get_error(self.__template_name)

    def __get_global_parameters_section(self):
        names = split(r'\s+', self.__global_parameters_name)
        lines = []
        for name in names:
            lines.extend(self.__section_lines.get(name))
        if lines:
            return parameters(clean_up_lines(lines))
        raise MissingSection.get_error(self.__global_parameters_name)

    def __get_repeater_parameters_section(self):
        query = create_query(self.__repeater_parameters_name)
        section_lines = (self.__section_lines.get(name) for name in query.names)
        csv_parameters = [
            TableParameters(clean_up_lines(lines))
            for lines in section_lines
        ]
        return query.query(csv_parameters)

    def print(self):
        for record in self.__repeater_parameters:
            record.update(self.__global_parameters)
            print(self.__template.generate(record), end='')

    def validate(self):
        self.__template.validate()

        repeater_parameters_names = set(self.__repeater_parameters[0].keys())
        prefixed_names = {name for name in repeater_parameters_names if name.find('.') > 0}
        non_prefixed_names = repeater_parameters_names - prefixed_names
        global_parameters_names = set(self.__global_parameters.keys())

        if global_parameters_names & non_prefixed_names:
            raise ValidationError.get_error('Name conflicts in global and repeater parameter sections')

        template_variables = self.__template.names
        undefined_template_variables = template_variables - (global_parameters_names | repeater_parameters_names)
        for undefined_variable in undefined_template_variables:
            duplicates = {name for name in repeater_parameters_names if name.endswith('.' + undefined_variable)}
            if duplicates:
                duplicates = {'"{}"'.format(duplicate) for duplicate in duplicates}
                raise ValidationError.get_error(
                    '"{}" in the template must be prefixed: {}'.format(undefined_variable, ' or '.join(duplicates))
                )
            else:
                raise ValidationError.get_error(
                    'Undefined variable in the template: "{}"'.format(undefined_variable)
                )

    def __get_config_parameters(self):
        config_section = self.__section_lines.get(self.__config_section)
        if config_section:
            config = parameters(clean_up_lines(config_section))
            self.__validate_config(config)
            return config
        raise MissingSection.get_error(self.__config_section)

    def __validate_config(self, config):
        missing_config_parameters = {TEMPLATE, GLOBAL_PARAMETERS, REPEATER_PARAMETERS} - set(config.keys())
        if missing_config_parameters:
            missing_parameters = ', '.join(missing_config_parameters)
            raise MissingParameter.get_error(missing_parameters, self.__config_section)
