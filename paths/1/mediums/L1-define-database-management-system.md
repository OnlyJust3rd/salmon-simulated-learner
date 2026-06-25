---
id: medium-define-database-management-system
outcome: L1-define-database-management-system
title: What Is a Database Management System
medium_type: text
---

A database management system, abbreviated DBMS, is the specialized software that
creates, maintains, and controls access to a database. Within the wider database
system — which also includes the data, the hardware, and the users — the DBMS is
specifically the program layer that stands between people or applications and the
stored data. Applications never read or write the underlying files directly;
instead they send requests to the DBMS, which interprets them, carries out the
necessary operations on the physical storage, and returns the results. In doing
so it hides the messy details of how and where the data actually lives,
presenting every user with a clean, consistent interface.

The DBMS exists to provide a set of services that would be difficult, repetitive,
and error-prone for each application to implement on its own. The first is data
definition: using a data definition language, designers describe the structure of
the data — what tables, fields, or collections exist and what rules they must
obey. The second is data manipulation: through a query language, most commonly
SQL in relational systems, users insert, retrieve, update, and delete data,
typically by describing what they want rather than how to obtain it.

Beyond these, a DBMS enforces data integrity, applying constraints so that
invalid data — a negative age, or an order referring to a customer who does not
exist — is refused. It manages concurrency control, allowing many users to
operate on the same data at the same time without interfering with one another; a
classic illustration is preventing two shoppers from each buying the last item in
stock. It provides security and authorization, granting or denying each user
permission to view or modify particular data, so that, for instance, only payroll
staff can change salaries. And it provides backup and recovery, keeping the
database consistent and restoring it to a correct state after a crash, a disk
failure, or a power cut.

A central capability of many database management systems is transaction
management. A transaction is a group of operations treated as a single,
indivisible unit of work. The DBMS guarantees that either all of a transaction's
operations take effect or none of them do, and that once a transaction is
confirmed its changes are permanent. This is what allows a money transfer — a
debit from one account and a credit to another — to be safe even if the system
fails halfway through.

It is useful to distinguish the DBMS from the database itself. The database is
the actual collection of stored data; the DBMS is the software engine that
manages it. In the same way that a single word-processing program can open many
documents, a single DBMS can manage many separate databases.

Database management systems come in several categories suited to different shapes
of data. Relational systems such as MySQL, PostgreSQL, Oracle, and Microsoft SQL
Server store data in tables and dominate business computing. Document-oriented
systems such as MongoDB store flexible, self-contained records. Graph systems
such as Neo4j store networks of connected entities. Each category offers the same
core management services but optimizes for a particular way of organizing
information. Users encounter a DBMS in two broad styles of use: day-to-day
operation, in which applications issue many small, fast read-and-write requests
such as recording a sale or updating a profile, known as transaction processing;
and analytical use, in which the same data is queried in large, complex ways to
discover patterns and support decisions.

In short, a database management system is the engine that turns a passive
collection of stored data into a reliable, shared, secure, and queryable
resource. Understanding the DBMS as the controlling software layer is essential
groundwork for studying the specific data models and products that build upon it.
