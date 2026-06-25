---
id: medium-define-relational-database
outcome: L1-define-relational-database
title: What Is a Relational Database
medium_type: text
---

A relational database is a database that organizes data into relations — more
familiarly called tables — following the relational model first proposed by the
computer scientist E. F. Codd in 1970. The model is built on simple, well-defined
ideas borrowed from mathematics, and its clarity and rigour are the reason it has
dominated data management for half a century. In a relational database, all data
is presented to the user as a collection of tables, and nothing else; there are
no hidden pointers or structures the user must navigate.

Each table represents one type of entity — for example students, courses,
products, or orders — and is made up of rows and columns. A row, known formally as
a tuple, is a single record describing one instance of the entity, such as one
particular student. A column, also called an attribute, describes one property of
the entity, such as the student's name or date of birth, and every value in that
column is drawn from a defined set of permitted values called a domain. The
structure of all the tables and the rules governing them — collectively the
schema — is fixed in advance, so every row in a table shares the same columns.

The real power of the relational model comes from how separate tables are linked
together through keys. A primary key is one or more columns whose values uniquely
identify each row in a table, guaranteeing that no two rows can be confused; a
student_id, for instance, identifies exactly one student. A foreign key is a
column in one table that refers to the primary key of another, and it is the
mechanism that records relationships. Suppose a Students table has student_id as
its primary key and an Enrolments table stores that same student_id as a foreign
key alongside a course code. The foreign key ties each enrolment back to exactly
one student, expressing the relationship "this student is enrolled in this
course." Because the student's full details are stored only once, in the Students
table, and merely referenced elsewhere, the data is not needlessly duplicated and
cannot fall out of agreement with itself.

This careful separation of data into related tables is supported by a design
discipline called normalization, which splits data into smaller tables to
eliminate redundancy and the update problems that redundancy causes. The result
is two major benefits. First, integrity rules — such as the requirement that
every foreign key must point to a real, existing row, known as referential
integrity — keep the data accurate and trustworthy. Second, because relationships
are captured explicitly, data from many tables can be recombined flexibly to
answer questions that were never anticipated when the database was designed.

The data is queried using a declarative language, almost always SQL, in which the
user describes the result they want rather than the step-by-step procedure to
compute it. A single query can draw together rows from several related tables —
listing each student next to the titles of the courses they take — by matching
foreign keys to primary keys, an operation called a join. The database engine is
then free to work out the most efficient way to produce the answer.

A familiar way to picture a relational database is as a set of linked
spreadsheets: each sheet is a table of rows and columns, and a shared identifier
in two sheets connects related rows. The analogy is imperfect — a true relational
database enforces types, keys, and integrity rules that a spreadsheet does not —
but it captures the essential grid-like shape. The relational database remains the
default choice for applications that require well-structured, consistent data
with strong guarantees of correctness, from banking and inventory to enrolment
and payroll, and it is the foundation on which relational database management
systems and the SQL language are built.
