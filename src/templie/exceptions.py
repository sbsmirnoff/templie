"""
Templie exceptions
"""


class DslSyntaxError(Exception):
    @classmethod
    def get_error(cls, line):
        return cls('invalid line: {}'.format(line.strip('\n')))