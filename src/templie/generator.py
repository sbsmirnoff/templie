"""
Templie output generation
"""

from shutil import copyfile

import os
import sys

from .section_lines import split_into_sections
from .sections import Sections


def generate(input_file_name, output_file_name):
    with open(input_file_name, 'r') as input_file:
        section_lines = split_into_sections(input_file)

    sections = Sections(section_lines)
    sections.validate()

    __backup_output_file(output_file_name)
    file = open(output_file_name, 'w') if output_file_name else sys.stdout
    with file as output_file:
        for record in sections.repeater_parameters:
            record.update(sections.global_parameters)
            output_file.write(sections.template.generate(record))


def __backup_output_file(output_file_name):
    if output_file_name and os.path.exists(output_file_name):
        copyfile(output_file_name, output_file_name + '~')
