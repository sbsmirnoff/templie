"""
Templie output generation
"""

from shutil import copyfile

import os

from .config_parameters import get_config_parameters
from .section_lines import split_into_sections
from .sections import Sections


def generate(input_file_name, output_file_name):
    with open(input_file_name, 'r') as input_file:
        section_lines = split_into_sections(input_file)

    config_parameters = get_config_parameters(section_lines)
    sections = Sections(section_lines, config_parameters)
    sections.validate()

    __backup_output_file(output_file_name)
    with open(output_file_name, 'w') as output_file:
        for record in sections.repeater_parameters:
            record.update(sections.global_parameters)
            output_file.write(sections.template.generate(record))


def __backup_output_file(output_file_name):
    if os.path.exists(output_file_name):
        copyfile(output_file_name, output_file_name + '~')
