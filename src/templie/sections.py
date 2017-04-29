"""
Sections class
"""

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
        config_parameters = self.get_config_parameters()
        self.__template_name = config_parameters[TEMPLATE]
        self.__global_parameters_name = config_parameters[GLOBAL_PARAMETERS]
        self.__repeater_parameters_name = config_parameters[REPEATER_PARAMETERS]
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
        query = create_query(self.__repeater_parameters_name)
        section_lines = (self.__section_lines.get(name) for name in query.names)
        csv_parameters = [
            TableParameters(clean_up_lines(lines))
            for lines in section_lines
        ]
        return query.query(csv_parameters)

    def validate(self):
        if not self.repeater_parameters:
            return

        self.template.validate()

        repeater_parameters_names = self.repeater_parameters[0].keys()
        global_parameters_names = set(self.global_parameters.keys())
        if global_parameters_names & repeater_parameters_names:
            raise ValidationError.get_error('Name conflicts in global and repeater parameter sections')

        template_variables = set(self.template.names)
        undefined_template_variables = template_variables - (global_parameters_names | repeater_parameters_names)
        if undefined_template_variables:
            raise ValidationError.get_error(
                'Undefined variables in the template: {}'.format(', '.join(undefined_template_variables))
            )

    def get_config_parameters(self):
        config_section = self.__section_lines.get(self.__config_section)
        if config_section:
            config = parameters(clean_up_lines(config_section))
            self.validate_config(config)
            return config
        raise MissingSection.get_error(self.__config_section)

    def validate_config(self, config):
        missing_config_parameters = {TEMPLATE, GLOBAL_PARAMETERS, REPEATER_PARAMETERS} - set(config.keys())
        if missing_config_parameters:
            missing_parameters = ', '.join(missing_config_parameters)
            raise MissingParameter.get_error(missing_parameters, self.__config_section)