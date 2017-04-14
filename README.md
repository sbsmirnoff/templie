# Templie

Templie is a lightweight DSL for creating multiple copies of a text generated from a parametrized template.
Suppose your are given a CSV file with the names of new employees in the sales department.

```
first_name;  last_name
Victor;      Lee
Sandra;      Dee
...
```

You need to make an SQL script to send to the DBA to register all these employees in the HR database.

```
INSERT INTO EMPLOYEE (ID, FIRST_NAME, LAST_NAME, DEPARTMENT)
VALUES (SEQ_EMPLOYEE.nextval, 'Victor', 'Lee', 'Sales');

INSERT INTO EMPLOYEE (ID, FIRST_NAME, LAST_NAME, DEPARTMENT)
VALUES (SEQ_EMPLOYEE.nextval, 'Sandra', 'Dee', 'Sales');

...
```