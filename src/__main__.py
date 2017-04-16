"""
Templie's main function
"""


from argparse import ArgumentParser, HelpFormatter

from templie import generate, TemplieException


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
    except TemplieException as e:
        print(e.args[0])

if __name__ == '__main__':
    __main()
