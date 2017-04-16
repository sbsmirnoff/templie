"""
Templie output generation
"""

from .section_lines import get_section_lines


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