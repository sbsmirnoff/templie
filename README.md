# Templie

Templie is a lightweight DSL for creating multiple copies of a text generated from a parametrized template.
Suppose you are given a CSV file with the names of new employees in your company's sales department.

```
first_name;  last_name
Bruce;       Lee
Sandra;      Dee
...
```

You have to make an SQL script to send to the DBA who will run it and register all these employees
in the HR database.

```
INSERT INTO EMPLOYEE (ID, FIRST_NAME, LAST_NAME, DEPARTMENT_ID)
VALUES (SEQ_EMPLOYEE.nextval, 'Bruce', 'Lee', (SELECT ID FROM DEPARTMENT WHERE NAME = 'Sales'));

INSERT INTO EMPLOYEE (ID, FIRST_NAME, LAST_NAME, DEPARTMENT_ID)
VALUES (SEQ_EMPLOYEE.nextval, 'Sandra', 'Dee', (SELECT ID FROM DEPARTMENT WHERE NAME = 'Sales'));

...
```

This is the sort of task that Templie helps automate.

## Getting started

To use Templie you need Python 3 installed on your machine.
Go to the project's root directory and build an executable by running

```
./build.sh
```

The executable file is now in `out/` folder. Running Templie is as simple as

```
./templie <input file> -c <config section name> [<config section name> ...]
```

The input file is a script that gets interpreted by Templie (you may want to check out an example
script: `example/example.templie`). The generated output is sent to `stdout`,
while all error messages are sent to `stderr` (it is up to you to redirect those streams to where you want them).
Config section names determine which parts of the script get interpreted.

A Templie script is split into sections. Each section starts with the
section's name inside square brackets (e.g. `[Template]`) and continues till
the end of the file or the start of the next section, whichever comes first.
The part of the input file that comes before the beginning of the first section is
entirely ignored by Templie. You can use it for whatever purpose you wish.

Section names are not allowed to contain whitespace characters.

There are three types of sections in Templie scripts: parameter sections, CSV sections and templates.

### Parameter sections

Parameter sections contain name value pairs, e.g

```
[some_parameter_section_name]

department = Sales
company_name = "Hewlett Packard Enterprise"
```

Only alphanumeric characters and underscores are allowed in parameter's names (the first character must not be a digit).
Parameter values that contain spaces have to be enclosed by double quotes.
The parameter names can then be used inside template sections as placeholders for their values.

### CSV sections

The second type is a CSV section. Those contain (just as the name suggests) comma (or semicolon or whitespace)
separated values of repeater parameters, e.g.

```
[some_repeater_parameter_section_name]

first_name, last_name

Leonhard Euler
"Johann Carl Friedrich"; Gauss
"Jules Henri" Poincaré
Andrey Kolmogorov
Alan, Turing
```

The first row must contain parameters' names, all the following rows then contain their values. Just as with
the first section type, parameter names can be used inside template sections as placeholders for their values.

### Template sections

A templates section contains text that will be repeated for each value row in the CSV section, all parameter
placeholders replaced by those parameter's values. A placeholder is a dollar sign `$` followed by the
parameter's name optionally enclosed by curly braces, e.g. `$first_name` or `${company_name}`.
Curly braces are necessary when the placeholder is immediately followed by an alphanumeric character or an underscore.

### Config sections

A config section is a special section of the first type that informs the Templie interpreter which sections in the script are
to be used when you run it. Templie scripts can contain as many sections of each type as you wish, therefore you need to
explicitly indicate those you want to be interpreted. The following three parameters have to be included
in every config section:

```
template = some_template_section_name
global_parameters = some_parameter_section_name
repeater_parameters = some_repeater_parameter_section_name
```

There can be several config sections within a script. You tell Templie which one to use through the command line parameters:
```
./templie <input file> -c <config section name> [<config section name> ...]
```

If you include more than one config section, Templie will interpret all of them sequentially. E.g. running

```
./templie some_script -c config_section_1 config_section_2
```

will produce the same result as running

```
./templie some_script -c config_section_1
./templie some_script -c config_section_2
```

### Comments

`#` character is used for comments: all characters on a line starting with `#` are ignored by Templie.
Template sections, however, cannot have comments.

## Multiple parameter sections

TODO

## Joining CSV sections

TODO