---
id: comp_009
title: Optimize query execution
miller_level: shows_how
parent_skill: skill_database_internals
---

A query optimizer chooses an efficient execution plan for a SQL query. It
estimates the cost of alternative plans using statistics about table size and
data distribution. Choosing the right join order and join algorithm dramatically
changes performance. The optimizer decides whether to use an index scan or a
full table scan for each access. A good plan minimizes total cost while still
returning the correct result.
