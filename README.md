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
VALUES (SEQ_EMPLOYEE.nextval, 'Victor', 'Lee', (SELECT ID FROM DEPARTMENT WHERE NAME = 'Sales'));

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

The input file is a script that gets interpreted by Templie. The generated output is sent to `stdout`,
while all error messages are sent to `stderr` (it is up to you to redirect those streams to where you want them).
Config section names determine which parts of the script get interpreted.

A Templie script is split into sections. Each section starts with the
section's name inside square brackets (e.g. `[Template]`) and continues till
the end of the file or the start of the next section, whichever comes first.
The part of the input file that comes before the beginning of the first section is
entirely ignored by Templie. You can use it for whatever purpose you wish.

There are three types of sections in Templie scripts: parameter sections, CSV sections and templates.

### Parameter section

Parameter sections contain name value pairs, e.g

```
department = Sales
company_name = "Hewlett Packard Enterprise"
```

Only alphanumeric and underscore characters are allowed in parameter's names (the first character must not be a digit).
Parameter values that contain spaces have to be enclosed by double quotes.
These parameter names can then be used inside template sections as placeholders for their values.

### CSV section

The second type is a CSV section. Those contain (just as the name suggests) comma (or semicolon or whitespace)
separated values of repeater parameters, e.g.

```
first_name,                  last_name
Leonhard                     Euler
"Johann Carl Friedrich";     Gauss
"Jules Henri"                Poincaré
Andrey                       Kolmogorov
Alan                         Turing

```

The first row must contain the names of the parameters, all the following rows then contain their values. Just as with
the first section type, parameter names can be used inside template sections as placeholders for their values.

### Template section


Check out an example templie script `example/example.templie`.