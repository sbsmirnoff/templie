#!/usr/bin/env python3

import os
from shutil import copyfile
from re import search
from re import finditer
from string import Template as StringTemplate
from argparse import ArgumentParser, HelpFormatter

IDENTIFIER_REGEX = r'[_a-zA-Z][_a-zA-Z0-9]*'


class Template:

    def __init__(self, content):
        self.content = content
        self.__string_template = StringTemplate(content)

    def get_names(self):
        matches = [
            match.group(1) if match.group(1) else match.group(2)
            for match in finditer(r'\$(?:(%s)|{(%s)})' % (IDENTIFIER_REGEX, IDENTIFIER_REGEX), self.content)
        ]
        return iter(matches)

    def generate(self, parameters):
        return self.__string_template.substitute(parameters)


class Repeater:

    def __init__(self, lines):
        cleaned_lines = list(clean_up_lines(lines))
        self.__number_of_columns = len(cleaned_lines[0].split())
        self.__lines = cleaned_lines[1:]
        self.__names = self.__parse_names(cleaned_lines[0])

    def __iter__(self):
        for line in self.__lines:
            yield self.__name_value_map(line)

    def get_names(self):
        return self.__names

    def __compound_regex(self, unit_regex):
        parts = [unit_regex] * self.__number_of_columns
        regex = r'[,; ]'.join(parts)
        return r'^{}$'.format(regex)

    def __parse_names(self, line):
        pattern = self.__compound_regex(r'\s*({})\s*'.format(IDENTIFIER_REGEX))
        match = search(pattern, line)
        if match:
            return match.groups()
        raise DslSyntaxError.get_error(line)

    def __parse_values(self, line):
        pattern = self.__compound_regex(r'\s*(?:([^,;" ]+)|"([^"]*)")\s*')
        match = search(pattern, line)
        if match:
            return [
                value if value else quoted_value
                for value, quoted_value in grouped(match.groups(), 2)
            ]
        raise DslSyntaxError.get_error(line)

    def __name_value_map(self, line):
        return {
            name: value
            for name, value in zip(self.__names, self.__parse_values(line))
        }


class Parameters:

    def __init__(self, lines):
        pairs = (self.__get_key_value_pair(line) for line in clean_up_lines(lines))
        self.__map = {name: value for name, value in pairs}

    def get_parameter(self, name):
        return self.__map.get(name)

    def get_names(self):
        return self.__map.keys()

    def get_parameters(self):
        return self.__map

    @staticmethod
    def __get_key_value_pair(line):
        match = search(r'^\s*({})\s*=\s*(?:([^" ]+)|"([^"]*)")\s*$'.format(IDENTIFIER_REGEX), line)
        if match:
            name, value, quoted_value = match.groups()
            return name, value if value else quoted_value
        raise DslSyntaxError.get_error(line)


class DslSyntaxError(Exception):
    @classmethod
    def get_error(cls, line):
        return cls('invalid line: {}'.format(line.strip('\n')))


def get_section(line):
    line_without_comment = strip_comments(line)
    match = search(r'^\s*\[(.+)\]\s*$', line_without_comment.strip())
    return match.group(1) if match else ''


def strip_comments(line):
    match = search(r'^([^"#]*|(?:[^"#]*"[^"]*"[^"#]*)+)#.*$', line)
    return match.group(1) if match else line


def get_section_lines(iterator):
    sections_lines = {}
    section = ''
    for line in iterator:
        new_section = get_section(line)
        if new_section:
            section = new_section
        elif section:
            lines = sections_lines.setdefault(section, [])
            lines.append(line)
    return sections_lines


def clean_up_lines(lines):
    lines_without_comments = (strip_comments(line) for line in lines)
    stripped = (line.strip() for line in lines_without_comments)
    return (line for line in stripped if line)


def grouped(iterable, n):
    group = []
    for i, line in enumerate(iterable):
        group.append(line)
        if (i+1) % n == 0:
            yield group
            group.clear()
    if group:
        yield group


def get_config_parameter(config, name):
    parameter = config.get_parameter(name)
    if parameter:
        return parameter
    print('Missing {} parameter in [CONFIG] section'.format(name))
    exit(1)


def get_config(sections):
    config_section = sections.get('CONFIG')

    if config_section:
        config = Parameters(config_section)
        template = get_config_parameter(config, 'template')
        global_parameters = get_config_parameter(config, 'global_parameters')
        repeater_parameters = get_config_parameter(config, 'repeater_parameters')

        return template, global_parameters, repeater_parameters

    print('Input file does not contain [CONFIG] section')
    exit(1)


def get_template(sections, template_section):
    lines = sections.get(template_section)
    if lines:
        return Template(''.join(lines))
    print('Missing template sections: [{}]'.format(template_section))
    exit(1)


def get_parameters(sections, global_parameters_section, constructor):
    lines = sections.get(global_parameters_section)
    if lines:
        return constructor(lines)
    print('Missing [{}] section'.format(global_parameters_section))
    exit(1)


def has_duplicates(iterable):
    return len(set(iterable)) != len(list(iterable))


def validate(template, global_parameters, repeater_parameters):
    if has_duplicates(repeater_parameters.get_names()):
        print('Name conflicts in repeater parameter section')
        exit(1)

    global_parameters_names = set(global_parameters.get_names())
    repeater_parameters_names = set(repeater_parameters.get_names())

    if global_parameters_names & repeater_parameters_names:
        print('Name conflicts in global and repeater parameter sections')
        exit(1)

    template_variables = set(template.get_names())
    undefined_template_variables = template_variables - (global_parameters_names | repeater_parameters_names)
    if undefined_template_variables:
        print('Undefined variables in the template: {}'.format(', '.join(undefined_template_variables)))
        exit(1)


def generate(input_file_name, output_file_name):
    with open(input_file_name, 'r') as input_file:
        sections = get_section_lines(input_file)

    template_section, global_parameters_section, repeater_parameters_section = get_config(sections)
    template = get_template(sections, template_section)
    global_parameters = get_parameters(sections, global_parameters_section, Parameters)
    repeater_parameters = get_parameters(sections, repeater_parameters_section, Repeater)
    validate(template, global_parameters, repeater_parameters)

    backup_output_file(output_file_name)
    with open(output_file_name, 'w') as output_file:
        for record in repeater_parameters:
            record.update(global_parameters.get_parameters())
            output_file.write(template.generate(record))


def backup_output_file(output_file_name):
    if os.path.exists(output_file_name):
        copyfile(output_file_name, output_file_name + '~')


def __get_args_parser():
    parser = ArgumentParser(
        description='This templating DSL is called templie...',
        formatter_class=lambda prog: HelpFormatter(prog, max_help_position=40)
    )
    parser.add_argument('-i', '--input', help='input file', required=True)
    parser.add_argument('-o', '--output', help='output file', required=True)

    return parser


def __main():
    args = __get_args_parser().parse_args()
    try:
        generate(args.input, args.output)
    except IOError as error:
        print(error)
    except DslSyntaxError as error:
        print(error.args[0])

if __name__ == '__main__':

    __main()
