---
id: medium-define-relational-database-management-system
outcome: L1-define-relational-database-management-system
title: What Is a Relational Database Management System
medium_type: text
---

A relational database management system, abbreviated RDBMS, is a database
management system designed specifically to create, store, and operate databases
that follow the relational model. Where the relational model is the theory — data
organized into tables of rows and columns, linked by keys — the RDBMS is the
working software that puts that theory into practice and enforces its rules. The
great majority of database systems encountered in everyday business computing are
relational database management systems, including MySQL, PostgreSQL, Oracle
Database, Microsoft SQL Server, and SQLite.

An RDBMS provides all the general services of any database management system —
data definition, querying, security, concurrency control, backup and recovery —
and adds to them the particular features that embody the relational model. Chief
among these is the enforcement of structural constraints. It guarantees primary
keys, so that each row in a table is uniquely identifiable and no duplicates slip
in. It enforces foreign keys, so that a reference from one table always points to
a real, existing row in another; this property, called referential integrity, is
what keeps related tables consistent. If a user tries to record an order for a
customer who does not exist, or to delete a customer who still has orders, the
RDBMS refuses the operation. It also enforces other constraints such as requiring
a field to be unique, to be non-empty, or to fall within an allowed range.

Users define and manipulate the data using SQL, the standard relational query
language, which every major RDBMS supports with only small variations. Through
SQL, designers create and alter the tables, and users select, insert, update, and
delete the rows, combining data from multiple tables with joins.

The defining guarantee of a serious RDBMS is transaction support, summarized by
the ACID properties. Atomicity ensures that a transaction — a group of operations
treated as one unit — either takes effect completely or not at all; if any part
fails, the whole is rolled back. Consistency ensures that a transaction moves the
database from one valid state to another, never leaving it half-changed.
Isolation ensures that concurrent transactions do not see one another's
incomplete work, so simultaneous users behave as if they were taking turns.
Durability ensures that once a transaction is committed, its changes survive even
a power loss or crash. The classic illustration is a bank transfer: the debit
from one account and the credit to another must both succeed or both fail, so
money is never created or destroyed midway, even if many transfers run at once
and the machine crashes in between.

To deliver these guarantees the RDBMS includes a number of internal mechanisms
that the user rarely sees but constantly relies on. A query optimizer analyses
each SQL statement and chooses an efficient plan for executing it. Indexes —
auxiliary data structures maintained by the system — let it find matching rows
quickly without scanning an entire table. A locking and concurrency-control
subsystem coordinates simultaneous transactions, and a logging and recovery
subsystem records changes so the database can be restored after a failure.

Because of this combination of structural integrity and strong transactional
guarantees, an RDBMS is the default choice whenever an application's data must
remain strictly correct, consistent, and well structured — in finance,
accounting, inventory, reservations, and official record-keeping. The trade-off
is that the rigid, predefined schema and strong guarantees can make relational
systems harder to scale across very many machines or to adapt to rapidly
changing, irregular data — the very situations that motivated the later NoSQL
systems. For the large class of applications where correctness matters most,
however, the relational database management system remains the standard tool, and
recognizing one means understanding it as the software that brings the relational
model to life.
