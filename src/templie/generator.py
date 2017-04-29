"""
Templie output generation
"""

from .section_lines import split_into_sections
from .sections import Sections


def generate(input_file_name, config_section_names):
    with open(input_file_name, 'r') as input_file:
        section_lines = split_into_sections(input_file)
    for config_section_name in config_section_names:
        _output(section_lines, config_section_name)


def _output(section_lines, config_section_name):
    sections = Sections(section_lines, config_section_name)
    sections.validate()

    for record in sections.repeater_parameters:
        record.update(sections.global_parameters)
        print(sections.template.generate(record), end='')
