---
id: medium-recognize-sql
outcome: L1-recognize-sql
title: What Is Structured Query Language
medium_type: text
---

Structured Query Language, universally abbreviated SQL, is the standard
programming language for defining, manipulating, and querying data held in
relational databases. It is the common tongue of the relational world: practically
every relational database management system — MySQL, PostgreSQL, Oracle, Microsoft
SQL Server, SQLite, and many more — understands SQL, with only minor differences
in dialect. This means that the core skill of writing SQL transfers from one
system to another, which is a large part of why SQL has remained one of the most
important and widely used languages in all of computing for decades.

SQL has a notable history. It was developed at IBM in the early 1970s, growing out
of Codd's relational model, and was originally called SEQUEL. It was standardized
by ANSI and ISO in 1986, and that standard has been revised many times since to
add new capabilities, while the language's core has remained remarkably stable.

A defining characteristic of SQL is that it is declarative rather than procedural.
The user describes what result they want, not the step-by-step procedure for
computing it. For example, the statement SELECT name FROM students WHERE class =
'6A' asks for the names of all students in class 6A; the user does not say how to
scan the data or in what order, leaving the database's query optimizer free to
determine the most efficient way to produce the answer. This separation of intent
from execution is part of what makes SQL both concise and powerful.

The language is conventionally divided into sublanguages according to purpose. The
Data Definition Language (DDL) creates and changes the structure of the database,
with commands such as CREATE TABLE to define a new table, ALTER TABLE to change
one, and DROP TABLE to remove one. The Data Manipulation Language (DML) works with
the data held inside those structures: SELECT retrieves rows, INSERT adds new
rows, UPDATE changes existing rows, and DELETE removes them. The Data Control
Language (DCL) manages permissions with GRANT and REVOKE, determining who may do
what. And transaction-control commands such as COMMIT and ROLLBACK group
statements into all-or-nothing units of work.

By far the most heavily used part of SQL is the SELECT statement, which retrieves
data and can express remarkably sophisticated questions. A SELECT lists the
columns wanted and the table they come from; a WHERE clause filters the rows to
only those meeting a condition, much like looping over every row and keeping the
ones for which the condition is true. Results can be sorted with ORDER BY, and
rows can be collapsed into summaries — counts, sums, and averages — with aggregate
functions and the GROUP BY clause, so that a single query can report, say, the
average grade in each class.

The feature that truly unlocks the relational model is the JOIN. Because related
data is deliberately spread across several tables, a join recombines it by
matching a foreign key in one table to the primary key in another. A query joining
a students table to a grades table can list each student alongside the subjects
and scores recorded for them, even though that information lives in two separate
places. Joins are what let a normalized, non-duplicated design still answer
questions that span many entities. SQL also supports subqueries — queries nested
inside other queries — and views, which are saved queries that behave like virtual
tables.

Because relational databases dominate business and data computing, and SQL is
their universal interface, fluency in it is one of the most broadly useful skills
in software development, data analysis, and data science. A solid grasp of SELECT
with WHERE and ORDER BY, the data-changing commands INSERT, UPDATE, and DELETE,
aggregation with GROUP BY, and the JOIN provides the foundation for almost all
everyday work with relational data. To recognize SQL is to know it as the
standard, declarative language through which people and programs communicate with
relational databases.
