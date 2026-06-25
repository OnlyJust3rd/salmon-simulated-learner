---
id: comp_006
title: Use indexes for fast access
miller_level: knows_how
parent_skill: skill_database_internals
---

An index is an auxiliary data structure that speeds up row lookup in a table. A
b-tree index keeps keys sorted so the database can search by range or by exact
match efficiently. Without an index the system must perform a full scan that
reads every row in the table. Indexes trade extra storage and slower writes for
much faster reads. Choosing which columns to index is central to database
performance tuning.
