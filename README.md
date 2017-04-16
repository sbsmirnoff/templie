# Templie

Templie is a lightweight DSL for creating multiple copies of a text generated from a parametrized template.
Suppose you are given a CSV file with the names of new employees in your company's sales department.

```
first_name;  last_name
Victor;      Lee
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

Go to the project's root directory and build an executable by running

```
./build.sh
```

The executable file is now in `out/` folder. Running Templie is as simple as

```
./templie -i <input file> -o <output file>
```

Check out an example templie script `example/example.templie`.