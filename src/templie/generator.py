"""
Templie output generation
"""

from .section_lines import split_into_sections
from .sections import Sections


def generate(input_file_name, config_section_names):
    with open(input_file_name, 'r') as input_file:
        section_lines = split_into_sections(input_file)
    for config_section_name in config_section_names:
        sections = Sections(section_lines, config_section_name)
        if sections.nonempty():
            sections.validate()
            sections.print()
