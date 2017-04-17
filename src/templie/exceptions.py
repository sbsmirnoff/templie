"""
Templie exceptions
"""


class TemplieException(Exception):
    pass


class DslSyntaxError(TemplieException):
    @classmethod
    def get_error(cls, line):
        return cls('invalid line: {}'.format(line.strip('\n')))


class MissingSection(TemplieException):
    @classmethod
    def get_error(cls, section):
        return cls('Input file does not contain [{}] section'.format(section))


class MissingParameter(TemplieException):
    @classmethod
    def get_error(cls, name, section):
        return cls('Missing {} in section [{}]'.format(name, section))


class WrongValue(TemplieException):
    @classmethod
    def get_error(cls, name, correct_value):
        return cls('Wrong value of the parameter {}: it must be {}'.format(name, correct_value))


class ValidationError(TemplieException):
    @classmethod
    def get_error(cls, message):
        return cls(message)
