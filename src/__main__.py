"""
Templie's main function
"""

from argparse import ArgumentParser

from templie import generate, TemplieException


def _get_args_parser():
    parser = ArgumentParser(description='This templating DSL is called templie...')
    parser.add_argument('input', help='input file')
    parser.add_argument('-c', nargs='+', help='config section', required=True)

    return parser


def __main():
    args = _get_args_parser().parse_args()
    try:
        generate(args.input, args.c)
    except IOError as error:
        print(error)
    except TemplieException as e:
        print(e.args[0])

if __name__ == '__main__':
    __main()
