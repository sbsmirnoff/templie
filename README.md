# Templie

Templie is a lightweight DSL for creating multiple copies of a text generated from a parametrized template.
Suppose you are given a CSV file with the names of new employees in the sales department.

```
first_name;  last_name
Victor;      Lee
Sandra;      Dee
...
```

You need to make an SQL script to send to the DBA who will run it and register all these employees
in the HR database.

```
INSERT INTO EMPLOYEE (ID, FIRST_NAME, LAST_NAME, DEPARTMENT_ID)
VALUES (SEQ_EMPLOYEE.nextval, 'Victor', 'Lee', (select ID from DEPARTMENT where NAME = 'Sales'));

INSERT INTO EMPLOYEE (ID, FIRST_NAME, LAST_NAME, DEPARTMENT)
VALUES (SEQ_EMPLOYEE.nextval, 'Sandra', 'Dee', (select ID from DEPARTMENT where NAME = 'Sales'));

...
```

This is the sort of task that Templie will help you automate.

## Getting started

Check out an example templie script `example/example.templie`.