---
id: medium-recognize-neo4j
outcome: L1-recognize-neo4j
title: Recognizing Neo4j
medium_type: text
---

Neo4j is the most widely used graph database and the standard example people meet
when learning how connected data can be stored and queried. Rather than placing
data in the tables of the relational model or the documents of a document store,
Neo4j represents information using the property-graph model: data is stored as
nodes, which stand for entities, and relationships (the graph term for edges),
which connect those nodes. Both nodes and relationships can hold properties —
key-value pairs that describe them — and nodes can be tagged with labels that
classify them, while every relationship has a type and a direction. A person node
might carry properties such as a name and an age, and a "PURCHASED" relationship
linking that person to a product might record the date and quantity of the
purchase.

Neo4j has been developed since the early 2000s by the company Neo4j, Inc., and was
among the systems that popularized the very term "graph database." It is available
as open-source community software and as a commercial enterprise edition, as well
as a managed cloud service, and it has become close to synonymous with the
category in the way that a leading product often does.

The central idea behind Neo4j, and the source of its performance, is that
relationships are stored directly and treated as first-class data. In a relational
database, a connection between two records is implied by matching a foreign key to
a primary key, and following a chain of connections requires repeatedly joining
large tables — work that grows more and more costly as the chains lengthen. Neo4j
instead stores each relationship as a concrete, physical link from one node to
another, an arrangement called index-free adjacency. As a result, traversing from
a node to its neighbours, and onward to their neighbours, is a direct local
operation whose cost depends only on how much of the graph is actually visited,
not on the total size of the database. This is what lets Neo4j answer deeply
connected questions — friends of friends, the shortest path between two people, or
a chain of suspicious transactions — quickly even across graphs of millions or
billions of nodes and relationships.

Neo4j is queried using Cypher, a declarative graph query language that Neo4j
created and later opened up, and which heavily influenced the new international
standard graph query language, GQL. Cypher is designed so that the pattern being
searched for is written almost like a small ASCII drawing of the graph: nodes
appear in parentheses and relationships as arrows between them. A pattern such as
(person)-[:FRIENDS_WITH]->(friend) reads naturally as "a person who is friends
with another person," and Neo4j finds every place in the graph where that shape
occurs. This makes graph queries unusually readable and expressive, especially
compared with writing the equivalent chain of joins in SQL.

Because of these strengths, Neo4j is applied wherever the relationships between
things are as important as the things themselves, and must be explored deeply and
quickly. Social networks model who is connected to whom and suggest new
connections from the shape of the network. Recommendation engines propose products
or content by following the links between users and the items they chose.
Fraud-detection systems uncover rings of accounts and suspicious chains of
transactions that are hard to see in tabular form. Other common uses include
knowledge graphs that power search and question answering, network and
IT-infrastructure management, identity and access management, and supply-chain and
logistics analysis.

The trade-off is that Neo4j is a specialized tool: for simple tabular data with
few relationships, a relational database is usually simpler, and for plain
high-volume key lookups other systems may be faster. Its advantage shines
precisely when connections are central. To recognize Neo4j is to identify it as
the flagship graph database, built around nodes, relationships, properties, and
the efficient traversal of connections expressed through the Cypher query
language.
