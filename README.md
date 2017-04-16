# Templie

Templie is a lightweight DSL for creating multiple copies of a text generated from a parametrized template.
Suppose you are given a CSV file with the names of new employees in the sales department.

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

Run Templie as follows

```
python templie.py -i <input file> -o <output file>
```

or (if templie.py is an executable)

```
./templie.py -i <input file> -o <output file>
```

Check out an example templie script `example/example.templie`.