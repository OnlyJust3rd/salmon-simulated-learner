---
id: medium-relation-data-model
outcome: L1-relation-data-model
title: What Is the Relational Data Model
medium_type: text
---

The relational data model is a formal, mathematically grounded way of describing
how data is organized, independent of how it is physically stored. It was
introduced by E. F. Codd at IBM in 1970 and has been the dominant model for
managing structured data ever since. Its central achievement is to give data a
simple, uniform structure — everything is presented as a collection of relations
— together with a rigorous theory for querying and constraining that data.

In the model's vocabulary, a relation is a set of records describing one kind of
thing, and it is usually pictured as a table. Each row of the table is a tuple, a
single record, and each column is an attribute, a named property whose values are
drawn from a fixed set of permitted values called a domain. Because a relation is
formally a set of tuples, two important consequences follow: no two rows are
identical, and the order of the rows carries no meaning. Likewise the columns are
identified by name rather than by position. This set-theoretic foundation is what
makes the model precise and lets it borrow results from mathematics.

A key distinction is between the schema and the instance. The schema is the fixed
description of a relation — its name and the columns it contains — while the
instance is the actual set of records present at a given moment. The schema is
designed once and changes rarely; the instance changes constantly as data is
inserted, updated, and deleted. Keeping the two separate is part of what gives a
relational system its stability and its data independence: applications are
written against the schema and are insulated from how the data is physically
arranged on disk.

Relationships between different relations are expressed not by pointers or nested
structures but by shared values. A candidate key is a minimal set of columns
whose values uniquely identify each record; one candidate key is chosen as the
primary key. A foreign key is a column in one relation whose values must match a
primary key in another, and this is how the model links, for example, an Orders
relation to the Customers relation. Representing relationships purely through
values, rather than physical links, is one of the model's defining ideas.

The model also builds in rules that keep data meaningful, called integrity
constraints. Entity integrity requires that no part of a primary key be empty, so
every record is identifiable. Referential integrity requires that every foreign
key value actually refer to an existing record, so links never dangle. Domain
constraints restrict each column to sensible values. These rules are part of the
model itself, not an afterthought left to applications.

Finally, the model comes with a precise theory of how to ask questions of the
data. Relational algebra defines a small set of operations — such as selecting
rows that meet a condition, projecting to chosen columns, and joining relations
on matching values — that take relations as input and produce relations as
output. Because every operation yields another relation, operations can be
composed freely. Relational calculus offers an equivalent, declarative way of
describing the desired result. Together they form the formal basis on which query
languages such as SQL are built.

It is worth distinguishing this model from a relational database: the model is
the abstract theory, while a relational database is an actual store of data
organized according to it, and a relational database management system is the
software that implements it. Understanding the model — relations, tuples,
attributes, keys, constraints, and the algebra over them — is what makes the
behaviour of every relational database comprehensible.
