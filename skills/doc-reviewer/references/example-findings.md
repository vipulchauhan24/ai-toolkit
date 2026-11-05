# Example Findings

Worked examples of each kind of finding, read by doc-reviewer when calibrating tone, quoting and severity.

Synthetic examples of correct format -- a design hole, an understanding hole, a hole of omission, a sleeper, and one finding that fails.

### A hole in the design

Doc text: "On checkout, the order service writes the order to MySQL and then publishes an OrderCreated event to Kafka for the downstream fulfilment and email services."

```
**fatal** partial failure

> "the order service writes the order to MySQL and then publishes an OrderCreated event to Kafka"

This is a dual write with no transactional boundary. When the MySQL commit succeeds and the Kafka publish fails -- broker unavailable, timeout, pod killed between the two calls -- the order exists but fulfilment and email never hear about it. The customer paid and nothing ships. Nothing in the doc detects or repairs this divergence.

Answer this: when the write succeeds and the publish fails, what notices, and how does the event get delivered?
```

### A hole in the understanding

Post text: "We moved the counter to Redis and increments became lock-free, so throughput went up 40x."

```
**serious** asserted, not shown

> "increments became lock-free, so throughput went up 40x"

The post never says what the increments were contending on before, so the reader cannot tell whether the 40x came from removing the lock, from moving off disk, or from Redis batching on the wire. The 40x also arrives with no client count, no payload, and no baseline configuration, so nobody can predict what they would get. A reader walks away believing "Redis is 40x faster than a database", which is not what was measured.

Answer this: what was the old increment path contending on?
```

### A hole of omission

Doc text: "Rollout: we will migrate all tenants to the new billing service on Saturday night."

```
**fatal** rollback

> Not addressed: how to return to the old billing service after the migration

Once tenants are invoiced by the new service, the invoices, credits, and payment states created after the cutover exist only there. If a billing bug shows up on Monday, switching the old service back on loses or duplicates those records. The doc does not say whether the migration is reversible after the first invoice run, or how long both systems stay in sync.

Answer this: what happens to records created in the new service if the old one must be restored on Monday?
```

### A sleeper

Doc text: "After each release, the on-call engineer updates the alert thresholds in the dashboard by hand."

```
**sleeper** human factors

> "the on-call engineer updates the alert thresholds in the dashboard by hand"

The thresholds are right only as long as someone remembers this step on every release. A Friday release or a new on-call engineer skips it, and the alert keeps the old threshold until an incident shows it is wrong. The doc names no check that notices a stale threshold.

Answer this: what tells anyone that a release shipped without the threshold update?
```

### A finding that fails

```
**serious** scale

> "the service handles requests from the mobile app"

This might not scale well and could become a bottleneck under load. Consider adding a cache.

Answer this: have you thought about scaling?
```

It fails on every rule: the quote is a description, not a claim; no component, number, or scenario is named; "consider adding a cache" is a fix; the question is not specific enough to close anything.

