"""
Splitting input file lines into sections
"""

from re import search

from .utils import strip_comments


def __get_section(line):
    line_without_comment = strip_comments(line)
    match = search(r'^\s*\[(.+)\]\s*$', line_without_comment.strip())
    return match.group(1) if match else ''


def get_section_lines(iterator):
    sections_lines = {}
    section = ''
    for line in iterator:
        new_section = __get_section(line)
        if new_section:
            section = new_section
        elif section:
            lines = sections_lines.setdefault(section, [])
            lines.append(line)
    return sections_lines
