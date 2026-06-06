# PostgreSQL Optimisation

PostgreSQL is the most capable open-source relational database. These techniques cover the most common performance bottlenecks.

## EXPLAIN ANALYZE
Always start with `EXPLAIN (ANALYZE, BUFFERS) <query>`. Look at:
- Actual rows vs estimated rows (planner accuracy).
- Seq Scan vs Index Scan.
- Buffer hits (cache) vs reads (disk).

## Index Types
- **B-tree**: default. Range queries, equality, ORDER BY.
- **GIN**: full-text search, array containment, JSONB keys.
- **GiST / SP-GiST**: geometric types, ranges.
- **BRIN**: append-only time-series tables — tiny index, moderate selectivity.
- **ivfflat / HNSW** (pgvector): approximate nearest-neighbour on vector columns.

## Partial Indexes
Index only the rows you query: `CREATE INDEX ON events (user_id) WHERE processed = false`. Dramatically smaller and faster than full indexes when the filtered subset is small.

## Connection Pooling
PostgreSQL forks a process per connection. Use PgBouncer (transaction mode) in front of the database. Keep the number of active server connections ≤ 4× CPU cores.

## VACUUM and Autovacuum
Dead tuples from UPDATE/DELETE accumulate and bloat tables. Autovacuum reclaims them. For write-heavy tables, tune `autovacuum_vacuum_scale_factor` and `autovacuum_cost_delay`.

## Partitioning
Range-partition large tables by time (e.g. created_at by month). Queries with a date filter skip irrelevant partitions entirely (partition pruning).

## Write-Ahead Log (WAL)
All writes go to the WAL first. `wal_buffers`, `checkpoint_completion_target`, and `synchronous_commit` are the key durability/performance levers.

## Query Tuning Checklist
1. Add indexes for columns in WHERE, JOIN ON, and ORDER BY.
2. Avoid `SELECT *`; fetch only needed columns.
3. Use CTEs (WITH clauses) for readability; PostgreSQL 12+ inlines them by default.
4. Batch INSERT with `COPY` or multi-row VALUES for bulk loads.
