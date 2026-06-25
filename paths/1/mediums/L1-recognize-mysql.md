---
id: medium-recognize-mysql
outcome: L1-recognize-mysql
title: Recognizing MySQL
medium_type: text
---

MySQL is one of the most widely used open-source relational database management
systems in the world, and for an enormous number of websites and applications it
is the database working quietly behind the scenes. Like any relational system, it
stores data in related tables of rows and columns and is queried using SQL. Its
enduring popularity rests on a particular combination of qualities: it is free and
open-source, it is fast and reliable for the common read-heavy workloads of web
applications, and it is comparatively easy to install, learn, and operate.
Together these have made MySQL both a default production database for countless
companies and a common first database for people learning the field.

MySQL has a notable history. It was created in the mid-1990s by a Swedish company,
MySQL AB, and its name combines "My" — the name of a co-founder's daughter — with
SQL. It was acquired by Sun Microsystems in 2008, which was in turn acquired by
Oracle Corporation in 2010, so MySQL is today an Oracle product, though it remains
open-source. Concern about that corporate ownership led some of the original
developers to create MariaDB, a community-driven fork that remains highly
compatible with MySQL and is itself widely used.

MySQL is especially associated with the web. It is the "M" in the classic LAMP
stack — Linux, Apache, MySQL, and PHP — the bundle of open-source software that
powered a large share of the early dynamic web, and it remains the database behind
hugely popular platforms, most famously WordPress, which stores its posts, users,
comments, and settings in MySQL tables. A developer can install MySQL and have a
working database within minutes, then connect to it from virtually any programming
language through well-established drivers. This low barrier to entry, combined with
vast amounts of documentation and community support, is a major reason for its
reach.

Despite a reputation for simplicity and speed, MySQL provides the features
expected of a serious relational database management system. Through its default
InnoDB storage engine it supports transactions with the full ACID guarantees
needed to keep data correct when many users act at once, and it enforces primary
and foreign keys to maintain referential integrity. It supports the standard SQL
features — joins, subqueries, views, and indexes — and offers tools for tuning
performance. MySQL is also known for its mature replication, in which copies of a
database are kept in sync so that many servers can share the load of read
requests, a technique that helps it scale to very high traffic; clustering options
extend this further.

Historically MySQL was sometimes criticized for favouring speed and ease over
strict standards compliance and advanced features, an area where PostgreSQL
traditionally led. Over successive versions, however, MySQL has closed much of
that gap, adding capabilities such as window functions, common table expressions,
and native support for storing JSON documents, so the practical distance between
the two systems has narrowed considerably.

In choosing between the two best-known open-source relational databases,
developers often reach for MySQL when they want a fast, reliable, easy-to-run
database for a web application with mostly straightforward, read-heavy needs, and
for PostgreSQL when they need its richer feature set and the strictest
correctness. Both are excellent, and the choice frequently comes down to ecosystem
and familiarity as much as raw capability.

To recognize MySQL, then, is to identify it as the archetypal open-source
relational database for web and general-purpose applications: table-based, queried
with SQL, transactionally safe through InnoDB, scalable through replication, and
chosen above all for its balance of speed, reliability, and ease of use. When you
picture a typical website saving users and orders into neat relational tables,
MySQL is one of the most likely engines doing the work, sitting alongside
PostgreSQL as one of the two open-source relational systems every practitioner
should know.
