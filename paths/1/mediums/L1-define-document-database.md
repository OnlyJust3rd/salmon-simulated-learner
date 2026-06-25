---
id: medium-define-document-database
outcome: L1-define-document-database
title: What Is a Document Database
medium_type: text
---

A document database is a type of NoSQL database that stores data as documents,
where each document is a self-contained record holding all the information about a
single item. It is one of the most popular NoSQL families because the document
closely matches how programmers already think about data in their code. Documents
are written in a structured, human-readable format — most commonly JSON
(JavaScript Object Notation) or a closely related binary encoding — and a document
can contain not only simple fields such as a name or a price, but also nested
objects and lists, allowing rich, hierarchical information to be expressed
naturally.

Related documents are gathered into a collection, which is roughly analogous to a
table in a relational database. The crucial difference is that the documents
inside a collection are not required to share an identical structure. One document
may contain fields that another omits, and a new field can be added to a single
document without touching any of the others. This is what is meant by a flexible
or "schema-less" design — though in practice the application still imposes an
informal structure; the database simply does not enforce a rigid one.

The contrast with the relational approach is illuminating. In a relational
database, a single customer's information might be deliberately split across
several tables — a customers table for the core details, an addresses table, and
an orders table — and reassembled when needed by joining those tables on shared
keys. This normalization avoids duplication but means that retrieving everything
about one customer requires combining several tables. In a document database, the
same customer is naturally stored as one document that embeds the address as a
nested object and the list of orders as an array of sub-documents. All the related
information lives together and can be read or written in a single operation,
without joins. This makes reads of a whole entity fast and intuitive, at the cost
of sometimes duplicating data that is shared between documents.

This model brings several practical advantages. Because the schema is flexible,
applications whose requirements change frequently can evolve their data without
the slow, disruptive migrations that altering a relational schema can require: a
new field such as loyalty_points can simply start appearing in new documents.
Because a document mirrors the structure of an object in a program, developers
spend less effort translating between the database and their code — a friction
that, in the relational world, is sometimes called the object–relational
impedance mismatch. And because each document is self-contained, the data can be
distributed across many servers relatively easily, supporting horizontal scaling.

There are trade-offs to weigh. The same flexibility that makes documents
convenient also shifts responsibility for consistency onto the application: with
no enforced schema, it is easier for malformed or inconsistent documents to creep
in. Data that is duplicated across many documents must be updated in many places.
And relationships that span documents are not enforced the way foreign keys are in
a relational system, so complex, highly interrelated data is often better served
by a relational or graph database.

Document databases are therefore well suited to applications whose data is
semi-structured, hierarchical, or changing quickly. Typical uses include content
management systems, product catalogs, user-profile and account stores, real-time
analytics, mobile application back ends, and the storage of event or log data. A
concrete example is a blog post stored as one document containing the title, the
author, the body text, a list of tags, and even an embedded array of comments —
everything needed to display the post retrievable in a single read. MongoDB is by
far the most widely used document database and the usual starting point for
learning this model, though others such as Couchbase and Amazon DocumentDB exist.
To recognize a document database is to identify it as the NoSQL family that stores
flexible, self-contained, JSON-like records grouped into collections.
