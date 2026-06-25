---
id: medium-define-graph-database
outcome: L1-define-graph-database
title: What Is a Graph Database
medium_type: text
---

A graph database is a type of NoSQL database that represents and stores data as a
graph — a collection of nodes connected by edges. It is built on a branch of
mathematics called graph theory, and its purpose is to make the relationships
between pieces of data as important, and as easy to work with, as the data itself.
In a graph database, a node stands for an entity, such as a person, a product, a
place, or an account, while an edge stands for a relationship between two
entities, such as "is friends with," "purchased," "is located in," or "reports
to."

Most graph databases use what is called the property-graph model, in which both
nodes and edges can carry properties — descriptive key-value pairs that store
details about them. A person node might hold properties such as a name and a birth
year, while a friendship edge connecting two people might hold the year the
friendship began. Edges are also typically directed and typed: a "FOLLOWS"
relationship points from one user to another and means something different in each
direction. This lets a graph capture not just that two things are connected, but
precisely how.

What fundamentally distinguishes a graph database from a relational one is that
relationships are stored directly, as first-class elements of the data, rather
than being reconstructed at query time. In a relational database, a relationship
is implied by matching a foreign key in one table to a primary key in another, and
answering a question that follows several relationships requires repeatedly
joining large tables. As the data grows, and as the questions reach further —
friends of friends, and their friends in turn — these joins become progressively
more expensive. A graph database instead stores each relationship as a concrete
link from one node to another, so following a connection is a direct, local step.
Traversing from a node to its neighbours, and then to their neighbours, stays
efficient even across millions of nodes and relationships, because the cost
depends on how much of the graph you actually walk, not on the total size of the
database. This property is sometimes called "index-free adjacency."

Graph databases are queried with specialized languages designed to describe
patterns of nodes and edges, rather than tables of rows. The most widely known is
Cypher, in which the pattern being searched for is written almost like a little
diagram: a query can ask for everyone matching a shape such as a person connected
by a "FRIENDS_WITH" edge to another person, and the database finds every place in
the graph where that shape occurs. Other graph query languages include Gremlin
and the emerging standard GQL.

Because of these strengths, graph databases are the natural choice for problems in
which the connections between data are as important as the data points
themselves, and in which those connections must be explored deeply and quickly.
Social networks are the archetypal example, modelling who is connected to whom and
recommending new connections from the structure of the network. Recommendation
engines suggest products or content by following the links between users and the
items they chose. Fraud-detection systems trace suspicious chains of transactions
and shared identities that would be hard to see in tabular form. Other common
applications include network and IT-infrastructure management, knowledge graphs
that power search and question answering, identity and access management, and
supply-chain and logistics modelling.

The trade-off is that graph databases are specialized: for simple, tabular data
with few relationships, a relational database is usually simpler and faster, and
graph databases are generally not aimed at the same high-volume, simple-lookup
workloads as key-value stores. Their advantage appears precisely when
relationships are central. Neo4j is the most widely used graph database and the
standard example of this model. To recognize a graph database is to identify it as
the NoSQL family built around nodes, edges, and the efficient traversal of
connections.
