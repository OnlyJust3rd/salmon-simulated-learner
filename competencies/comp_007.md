---
id: comp_007
title: Reason about transactions and ACID
miller_level: knows
parent_skill: skill_database_internals
---

A transaction is a unit of work that groups several database operations
together. Atomicity guarantees that either all of its operations commit or none
take effect, undone by rollback. Consistency ensures a transaction moves the
database from one valid state to another valid state. Isolation keeps concurrent
transactions from observing each other's intermediate state. Durability
guarantees that once a transaction commits its changes survive a crash.
