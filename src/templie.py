#!/usr/bin/env python3

import os
from shutil import copyfile
from re import search
from re import split
from re import finditer
from string import Template as StringTemplate
from argparse import ArgumentParser, HelpFormatter

IDENTIFIER_REGEX = r'[_a-zA-Z][_a-zA-Z0-9]*'
CONFIG_SECTION = 'CONFIG'
TEMPLATE_SECTION_PARAMETER = 'template'
GLOBAL_PARAMETERS_SECTION_PARAMETER = 'global_parameters'
REPEATER_PARAMETERS_SECTION_PARAMETER = 'repeater_parameters'
FLAT_REPEATER_PARAMETER = 'flat_repeater'


class Template:

    def __init__(self, content, name):
        self.__content = content
        self.__name = name
        self.__string_template = StringTemplate(content)

    def get_names(self):
        matches = [
            match.group(1) if match.group(1) else match.group(2)
            for match in finditer(r'\$(?:(%s)|{(%s)})' % (IDENTIFIER_REGEX, IDENTIFIER_REGEX), self.__content)
        ]
        return iter(matches)

    def generate(self, params):
        return self.__string_template.substitute(params)

    def validate(self):
        match = search(r'\$\s', self.__content)
        if match:
            msg = "{} contains a standalone delimiter '$'. Use '$$' if you want a dollar sign in your template"
            raise DslSyntaxError(msg.format(self.__name))


class RepeaterParameters:

    def __init__(self, lines, flat):
        cleaned_lines = list(clean_up_lines(lines))
        self.__number_of_columns = len(split(r'\s*,\s*|\s*;\s*|\s+', cleaned_lines[0]))
        self.__lines = cleaned_lines[1:]
        self.__lines = self.__get_lines(cleaned_lines[1:], flat)
        self.__names = self.__parse_names(cleaned_lines[0])

    def __iter__(self):
        for line in self.__lines:
            yield self.__name_value_map(line)

    def get_names(self):
        return self.__names

    def __get_lines(self, lines, flat):
        if flat:
            quoted = (self.__quote(line) for line in lines)
            return [','.join(group) for group in grouped(quoted, self.__number_of_columns)]
        else:
            return lines

    @staticmethod
    def __quote(line):
        if bool(search(r'^".*"$', line)):
            return line
        else:
            return '"{}"'.format(line)

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


class DslSyntaxError(Exception):
    @classmethod
    def get_error(cls, line):
        return cls('invalid line: {}'.format(line.strip('\n')))


def get_key_value_pair(line):
    match = search(r'^\s*({})\s*=\s*(?:([^" ]+)|"([^"]*)")\s*$'.format(IDENTIFIER_REGEX), line)
    if match:
        name, value, quoted_value = match.groups()
        return name, value if value else quoted_value
    raise DslSyntaxError.get_error(line)


def parameters(lines):
    pairs = (get_key_value_pair(line) for line in clean_up_lines(lines))
    return {name: value for name, value in pairs}


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
    parameter = config.get(name)
    if parameter:
        return parameter
    print('Missing {} parameter in [{}] section'.format(name, CONFIG_SECTION))
    exit(1)


def get_config(sections):
    config_section = sections.get(CONFIG_SECTION)

    if config_section:
        config = parameters(config_section)
        template = get_config_parameter(config, TEMPLATE_SECTION_PARAMETER)
        global_parameters = get_config_parameter(config, GLOBAL_PARAMETERS_SECTION_PARAMETER)
        repeater_parameters = get_config_parameter(config, REPEATER_PARAMETERS_SECTION_PARAMETER)
        is_flat_repeater = get_whether_flat_repeater(config)

        return template, global_parameters, repeater_parameters, is_flat_repeater

    print('Input file does not contain [{}] section'.format(CONFIG_SECTION))
    exit(1)


def get_whether_flat_repeater(config):
    flat = config.get(FLAT_REPEATER_PARAMETER, 'false')
    if flat == 'false':
        return False
    elif flat == 'true':
        return True
    else:
        raise DslSyntaxError.get_error('{} parameter must be either "true" or "false"'.format(FLAT_REPEATER_PARAMETER))


def get_template(sections, template_section):
    lines = sections.get(template_section)
    if lines:
        return Template(''.join(lines), template_section)
    print('Missing template sections: [{}]'.format(template_section))
    exit(1)


def get_global_parameters(sections, global_parameters_section):
    lines = sections.get(global_parameters_section)
    if lines:
        return parameters(lines)
    print('Missing global parameters section: [{}]'.format(global_parameters_section))
    exit(1)


def get_repeater_parameters(sections, repeater_parameters_section, flat):
    lines = sections.get(repeater_parameters_section)
    if lines:
        return RepeaterParameters(lines, flat)
    print('Missing repeater parameters section: [{}]'.format(repeater_parameters_section))
    exit(1)


def has_duplicates(iterable):
    return len(set(iterable)) != len(list(iterable))


def validate_parameters(template, global_parameters, repeater_parameters):
    if has_duplicates(repeater_parameters.get_names()):
        print('Name conflicts in repeater parameter section')
        exit(1)

    global_parameters_names = set(global_parameters.keys())
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

    template_section, global_parameters_section, repeater_parameters_section, is_flat_repeater = get_config(sections)
    template = get_template(sections, template_section)
    global_parameters = get_global_parameters(sections, global_parameters_section)
    repeater_parameters = get_repeater_parameters(sections, repeater_parameters_section, is_flat_repeater)
    validate_parameters(template, global_parameters, repeater_parameters)
    template.validate()

    backup_output_file(output_file_name)
    with open(output_file_name, 'w') as output_file:
        for record in repeater_parameters:
            record.update(global_parameters)
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
