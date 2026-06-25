---
id: medium-recognize-mongodb
outcome: L1-recognize-mongodb
title: Recognizing MongoDB
medium_type: text
---

MongoDB is the most widely used document database and, for a great many
developers, the first NoSQL system they ever encounter. Instead of storing data in
the rows and columns of a relational table, MongoDB stores it as documents in a
flexible, JSON-like format. To the developer a document looks like a familiar
object — a set of field-and-value pairs that can include nested objects and arrays
— and internally MongoDB stores these documents in an efficient binary encoding
called BSON (Binary JSON), which extends JSON with additional data types such as
dates and binary data. Each document holds all the fields describing a single
item, and related documents are gathered into a collection, which plays a role
similar to a table in a relational database.

The name "MongoDB" comes from the word humongous, reflecting its original design
goal of handling very large amounts of data, and the database first appeared
around 2009. It is developed by the company MongoDB, Inc., is available both as
open-source software you run yourself and as a fully managed cloud service called
MongoDB Atlas, and has grown into one of the most popular databases of any kind.

The defining advantage of MongoDB is its flexible schema. Documents within the
same collection are not required to share the same fields, so one product document
might include a discount field that another omits, and entirely new fields can be
introduced over time without rebuilding existing data or taking the database
offline. This makes MongoDB especially well suited to applications whose
requirements evolve quickly or whose data is naturally semi-structured —
situations in which the slow, disruptive schema migrations of a rigid relational
database would be a burden. A concrete example makes the model vivid: a blog post
can be stored as a single MongoDB document containing the title, the author, the
body text, a list of tags, and even an embedded array of comments, so that
everything needed to display the post is retrieved in one read rather than
assembled from several tables with joins.

This document-centric design carries several practical benefits. Because a
document closely resembles an object in application code, developers find that
little translation is needed between the program and the database, which speeds up
development — there is no object–relational impedance mismatch to fight. Because
related data is embedded together, reads of a whole entity are fast and simple.
And because documents are self-contained, MongoDB can distribute a collection
across many servers through a technique called sharding, in which the data is
partitioned by a chosen key so that the system can scale horizontally to very
large volumes and high throughput; it also supports replica sets, keeping copies
of the data for high availability and automatic failover.

MongoDB is queried not with SQL but with its own document-oriented query language
and an expressive aggregation pipeline that filters, groups, and transforms
documents in stages. Early in its history MongoDB was sometimes criticized for
favouring availability and speed over strict consistency and for lacking
multi-document transactions, but more recent versions have added support for ACID
transactions spanning multiple documents, narrowing the gap with relational
systems for applications that occasionally need stronger guarantees.

The flexibility that makes MongoDB convenient also shifts some responsibility onto
the application: with no enforced schema, keeping documents consistent is the
developer's job, and data duplicated across documents must be maintained in
several places. For highly interrelated data with many relationships, a relational
or graph database is often a better fit. Used for what it does best, however,
MongoDB excels. Typical applications include content management systems, product
catalogs, user-profile and account stores, real-time analytics, mobile and
Internet-of-Things back ends, and the storage of event and log data. To recognize
MongoDB is to know it as the leading NoSQL document database: schema-flexible,
document- and BSON-oriented, horizontally scalable through sharding, and a common,
productive choice for fast-moving, data-rich applications.
