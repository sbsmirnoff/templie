"""
CONFIG section
"""

from .exceptions import WrongValue, MissingSection, MissingParameter
from .sections import parameters


class Config:

    CONFIG_SECTION = 'CONFIG'
    TEMPLATE_SECTION_PARAMETER = 'template'
    GLOBAL_PARAMETERS_SECTION_PARAMETER = 'global_parameters'
    REPEATER_PARAMETERS_SECTION_PARAMETER = 'repeater_parameters'
    FLAT_REPEATER_PARAMETER = 'flat_repeater'

    def __init__(self, sections):
        config_section = sections.get(self.CONFIG_SECTION)
        if config_section:
            self.__config = parameters(config_section)
            self.template = self.__get_config_parameter(self.TEMPLATE_SECTION_PARAMETER)
            self.global_parameters = self.__get_config_parameter(self.GLOBAL_PARAMETERS_SECTION_PARAMETER)
            self.repeater_parameters = self.__get_config_parameter(self.REPEATER_PARAMETERS_SECTION_PARAMETER)
            self.is_flat_repeater = self.__get_whether_flat_repeater()
        else:
            raise MissingSection.get_error(self.CONFIG_SECTION)

    def __get_config_parameter(self, name):
        parameter = self.__config.get(name)
        if parameter:
            return parameter
        raise MissingParameter.get_error(name, self.CONFIG_SECTION)

    def __get_whether_flat_repeater(self):
        flat = self.__config.get(self.FLAT_REPEATER_PARAMETER, 'false')
        if flat == 'false':
            return False
        elif flat == 'true':
            return True
        else:
            raise WrongValue.get_error(self.FLAT_REPEATER_PARAMETER, 'either "true" or "false"')
