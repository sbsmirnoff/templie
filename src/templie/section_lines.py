"""
Splitting input file lines into sections
"""

from re import search

from .utils import strip_comments
from .exceptions import MissingSection


def _get_section(line):
    line_without_comment = strip_comments(line)
    match = search(r'^\s*\[(\S+)\]\s*$', line_without_comment.strip())
    return match.group(1) if match else ''


def _create_section_lines(iterable):
    sections_lines = {}
    section = ''
    for line in iterable:
        new_section = _get_section(line)
        if new_section:
            section = new_section
            sections_lines[section] = []
        elif section:
            sections_lines[section].append(line)
    return sections_lines


def split_into_sections(iterable):
    sections_lines = _create_section_lines(iterable)

    def get_lines(section_name):
        if section_name in sections_lines:
            return sections_lines[section_name]
        raise MissingSection.get_error(section_name)

    return get_lines
