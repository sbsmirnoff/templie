"""
Templie utilities functions
"""

from re import search


def grouped(iterable, n):
    group = []
    for i, line in enumerate(iterable):
        group.append(line)
        if (i+1) % n == 0:
            yield group
            group.clear()
    if group:
        yield group


def clean_up_lines(lines):
    stripped = (strip_comments(line).strip() for line in lines)
    return (line for line in stripped if line)


def strip_comments(line):
    match = search(r'^([^"#]*|(?:[^"#]*"[^"]*"[^"#]*)+)#.*$', line)
    return match.group(1) if match else line


def lines_to_csv(lines, number_of_columns):
    quoted = (__quote(line) for line in lines)
    return [','.join(group) for group in grouped(quoted, number_of_columns)]


def __quote(line):
    if bool(search(r'^".*"$', line)):
        return line
    else:
        return '"{}"'.format(line)
