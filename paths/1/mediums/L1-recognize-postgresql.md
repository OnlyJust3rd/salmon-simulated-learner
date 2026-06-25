---
id: medium-recognize-postgresql
outcome: L1-recognize-postgresql
title: Recognizing PostgreSQL
medium_type: text
---

PostgreSQL, very often shortened to "Postgres," is a powerful open-source
relational database management system renowned for its correctness, reliability,
standards compliance, and unusually rich set of features. Among open-source
databases it has a reputation as the choice of those who want their data handled
rigorously and who value capability over minimalism, and over the past decade it
has become one of the most popular and admired databases in the industry. Like any
relational system, it stores data in related tables of rows and columns and is
queried with SQL, adhering more closely to the official SQL standard than most of
its competitors.

PostgreSQL has deep roots. It grew out of the POSTGRES research project led by
Michael Stonebraker at the University of California, Berkeley, in the mid-1980s,
itself a successor to the earlier Ingres project. The "QL" was added when SQL
support was introduced, and since the mid-1990s the system has been developed by a
large, independent global community rather than owned by any single corporation.
That community governance, and the absence of a single commercial owner who might
restrict it, are themselves reasons many organizations favour it.

What truly sets PostgreSQL apart is how far it extends beyond the basics of the
relational model while still honouring them. It supports an exceptionally wide
range of data types, including arrays, ranges, geometric types, and key-value
pairs, and crucially it can store and query JSON and JSONB documents directly.
This last capability lets a single PostgreSQL database combine rigid,
well-structured relational tables with flexible, document-style data — in effect
offering some of the convenience of a NoSQL document store within a fully
relational system. It offers built-in full-text search for finding words within
large bodies of text, and through the celebrated PostGIS extension it becomes a
first-class geographic and spatial database used in mapping and location
applications. Above all, PostgreSQL is extensible by design: developers can define
their own data types, operators, functions, procedural languages, and even custom
index methods, and a large ecosystem of extensions builds on this foundation.

Underpinning these features are strong guarantees and sophisticated internals.
PostgreSQL provides full transactional integrity with the ACID properties, and it
implements an advanced form of concurrency control called multiversion concurrency
control (MVCC), which allows many users to read and write simultaneously without
unnecessary blocking — readers do not block writers and writers do not block
readers. It includes a capable query planner and optimizer, supports complex
queries, window functions, common table expressions, and a variety of indexing
strategies, and handles large data volumes and demanding analytical workloads
well. These qualities make it a favourite not only for transactional applications
but also for data warehousing and analytics, and a popular foundation for
specialized data platforms built on top of it.

There are trade-offs. PostgreSQL's richness can make it somewhat more complex to
configure and tune than a deliberately simpler system, and for the most basic
read-heavy web workloads a lighter database may be easier to operate. Historically
its out-of-the-box replication and clustering lagged behind some rivals, though
modern versions have strong replication and high-availability options. For the
large class of applications that value correctness and capability, these costs are
modest.

In the common comparison with MySQL, the other leading open-source relational
database, PostgreSQL is generally the choice when an application needs the
strictest standards compliance, advanced data types, complex queries, or the
flexibility of mixing relational and JSON data, while MySQL is often chosen for
simple, fast, read-heavy web serving. Both are first-rate, and the gap between
them has narrowed over time. To recognize PostgreSQL is to identify it as the
feature-rich, standards-focused, community-governed open-source relational
database — the system reached for when an application needs both the strict
guarantees of the relational model and flexibility well beyond plain tables. It is
consistently named together with MySQL as one of the two open-source relational
options every practitioner should know.
