---
id: medium-define-nosql
outcome: L1-define-nosql
title: What Is a NoSQL Database
medium_type: text
---

A NoSQL database is any database that stores and retrieves data using a model
other than the tables of rows and columns that define the relational model. The
name is usually read as "not only SQL," and that reading matters: NoSQL systems
are intended as an alternative and a complement to relational databases for
particular situations, not as a wholesale replacement for them. They rose to
prominence in the late 2000s, driven by the needs of large web companies whose
data had outgrown what a single relational server could comfortably handle.

NoSQL databases emerged to address several situations in which the strict
structure of relational tables becomes awkward. The first is irregular or rapidly
evolving data: when different records naturally have different fields, or when the
shape of the data changes frequently, forcing everything into one fixed table
schema is cumbersome. The second is sheer scale: when data must be spread across
hundreds or thousands of servers to handle enormous volumes and traffic, the
strong consistency guarantees of a single relational database become a
bottleneck. The third is developer speed: applications often want to store data
in a shape close to the objects in their code, without an elaborate up-front
schema design.

Rather than being a single design, NoSQL is an umbrella term covering several
distinct families, each suited to a different shape of data. Document databases
store each record as a self-contained, flexible document, typically in a JSON-like
format; MongoDB is the best-known example, and this family suits semi-structured
data such as user profiles and product catalogs. Key-value stores keep the
simplest possible structure — a unique key paired with an opaque value — and are
prized for their raw speed, making them ideal for caching and session storage;
Redis is a familiar example. Wide-column or column-family stores, such as
Cassandra, organize data by columns and are built to spread enormous tables
across many machines. Graph databases store data as nodes and the relationships
connecting them, making them ideal for highly connected information such as social
networks; Neo4j is a leading example.

The common thread running through these families is a relaxation of the strict,
predefined schema that relational systems require. In a relational table, every
row must share exactly the same columns, fixed in advance. In many NoSQL systems
each record may carry its own set of fields, so the structure can grow or vary
from record to record, and new fields can be introduced without rebuilding the
existing data. This flexibility, together with the ability to scale horizontally
by simply adding more commodity servers, is the central appeal of NoSQL.

These advantages, however, come with trade-offs, which are often framed through
the CAP theorem. The theorem observes that a distributed data store cannot
simultaneously guarantee perfect consistency, availability, and tolerance of
network partitions, and must trade some of one for the others. Many NoSQL systems
deliberately relax strict consistency in favour of availability and partition
tolerance, adopting a model often called "eventual consistency," in which
different copies of the data may disagree briefly before converging. For a banking
ledger this would be unacceptable, but for a social-media feed or a product
recommendation it is perfectly tolerable, and the gain in scale and speed is well
worth it.

In practice, the relational and NoSQL worlds increasingly overlap: relational
systems have added flexible JSON columns, and many real systems use both kinds of
database side by side, each for what it does best. NoSQL databases are widely used
in social networks, content platforms, real-time analytics, mobile applications,
and other fast-growing, data-intensive services. To understand NoSQL is to
recognize it not as a single technology but as a broad category of non-relational
databases, united by schema flexibility and horizontal scalability, and divided
into document, key-value, wide-column, and graph families.
