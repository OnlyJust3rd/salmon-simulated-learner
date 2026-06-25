---
id: comp_010
title: Recover from failure with logging
miller_level: shows_how
parent_skill: skill_database_internals
---

Database recovery restores a consistent state after a crash or other failure. A
write-ahead log records every change before it is applied to the data files.
During recovery the system replays committed changes with redo and reverses
uncommitted ones with undo. A checkpoint periodically flushes data so recovery
need not scan the entire log. Recovery is what ultimately delivers the
durability promised by the transaction model.
