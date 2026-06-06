# System Design Fundamentals

System design interviews and real architecture decisions share the same vocabulary. These are the key concepts.

## Scalability
- **Vertical scaling**: add CPU/RAM to one machine. Simple, limited.
- **Horizontal scaling**: add more machines. Requires stateless services or distributed state.

## Load Balancing
Distributes traffic across multiple servers. Round-robin, least-connections, and consistent hashing are common algorithms. L4 (TCP) load balancers are faster; L7 (HTTP) balancers support routing by URL/header.

## Caching
Reduces database load and latency. Cache at the application layer (Redis), at the CDN (static assets), or in the database (query cache, buffer pool).
- **Cache-aside**: application loads from cache; on miss, loads from DB and populates cache.
- **Write-through**: write to cache and DB simultaneously.
- **TTL vs invalidation**: TTL is simple; event-driven invalidation is fresh but complex.

## Message Queues
Decouple producers and consumers. Enable async processing, retries, and fan-out. Kafka for high-throughput streaming. RabbitMQ/SQS for task queues. NATS for lightweight pub-sub.

## Databases at Scale
- **Read replicas**: offload reads from the primary.
- **Sharding**: partition data across multiple DB instances by a shard key. Complex; avoid until necessary.
- **CQRS**: separate read and write models. Write to a normalised store; read from a denormalised projection.

## CAP Theorem
A distributed system can guarantee at most two of: Consistency, Availability, Partition tolerance. In practice, partition tolerance is non-negotiable, so systems choose between CP (strong consistency, may be unavailable under partition) and AP (always available, may return stale data).

## Observability
Logs + metrics + traces. Use structured JSON logs (not printf). Prometheus + Grafana for metrics. OpenTelemetry for distributed tracing. Alert on error rate and latency percentiles (p99), not just averages.
