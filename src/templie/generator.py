"""
Templie output generation
"""

import os
from shutil import copyfile

from .sections import Template, RepeaterParameters, parameters
from .section_lines import get_section_lines
from .config_parameters import Config
from .exceptions import MissingSection, ValidationError


def generate(input_file_name, output_file_name):
    with open(input_file_name, 'r') as input_file:
        sections = get_section_lines(input_file)

    config = Config(sections)
    template = __get_template(sections, config.template)
    global_parameters = __get_global_parameters(sections, config.global_parameters)
    repeater_parameters = __get_repeater_parameters(sections, config.repeater_parameters, config.is_flat_repeater)
    __validate_parameters(template, global_parameters, repeater_parameters)
    template.validate()

    __backup_output_file(output_file_name)
    with open(output_file_name, 'w') as output_file:
        for record in repeater_parameters:
            record.update(global_parameters)
            output_file.write(template.generate(record))


def __get_template(sections, template_section):
    lines = sections.get(template_section)
    if lines:
        return Template(''.join(lines), template_section)
    raise MissingSection.get_error(template_section)


def __get_global_parameters(sections, global_parameters_section):
    lines = sections.get(global_parameters_section)
    if lines:
        return parameters(lines)
    raise MissingSection.get_error(global_parameters_section)


def __get_repeater_parameters(sections, repeater_parameters_section, flat):
    lines = sections.get(repeater_parameters_section)
    if lines:
        return RepeaterParameters(lines, flat)
    raise MissingSection.get_error(repeater_parameters_section)


def __has_duplicates(iterable):
    return len(set(iterable)) != len(list(iterable))


def __validate_parameters(template, global_parameters, repeater_parameters):
    if __has_duplicates(repeater_parameters.get_names()):
        raise ValidationError.get_error('Name conflicts in repeater parameter section')

    global_parameters_names = set(global_parameters.keys())
    repeater_parameters_names = set(repeater_parameters.get_names())

    if global_parameters_names & repeater_parameters_names:
        raise ValidationError.get_error('Name conflicts in global and repeater parameter sections')

    template_variables = set(template.get_names())
    undefined_template_variables = template_variables - (global_parameters_names | repeater_parameters_names)
    if undefined_template_variables:
        raise ValidationError.get_error(
            'Undefined variables in the template: {}'.format(', '.join(undefined_template_variables))
        )


def __backup_output_file(output_file_name):
    if os.path.exists(output_file_name):
        copyfile(output_file_name, output_file_name + '~')
