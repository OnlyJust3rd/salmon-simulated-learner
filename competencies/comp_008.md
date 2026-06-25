---
id: comp_008
title: Apply concurrency control
miller_level: shows_how
parent_skill: skill_database_internals
---

Concurrency control coordinates transactions that run at the same time. A lock
prevents two transactions from writing the same row simultaneously.
Serializability is the correctness goal where concurrent execution matches some
serial order of the transactions. A deadlock arises when transactions each wait
on locks held by the other. Isolation levels let the system trade strict
consistency for higher concurrent throughput.
