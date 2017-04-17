"""
CONFIG section
"""

from .exceptions import MissingSection, MissingParameter
from .sections import parameters
from .sections import CONFIG_SECTION, TEMPLATE, GLOBAL_PARAMETERS, REPEATER_PARAMETERS


def get_config_parameters(sections):
    config_section = sections.get(CONFIG_SECTION)
    if config_section:
        config = parameters(config_section)
        validate_config(config)
        return config
    raise MissingSection.get_error(CONFIG_SECTION)


def validate_config(config):
    missing_config_parameters = {TEMPLATE, GLOBAL_PARAMETERS, REPEATER_PARAMETERS} - set(config.keys())
    if missing_config_parameters:
        missing_parameters = ', '.join(missing_config_parameters)
        raise MissingParameter.get_error(missing_parameters, CONFIG_SECTION)
