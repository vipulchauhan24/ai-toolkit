# Why we cache user profiles

In today's fast-paced world, it is important to note that performance really matters. In this post we are going to explore how we cache user profiles. Basically, a large number of requests hit the profile endpoint — and this is quite a problem.

## The problem

There are many requests that read the same profile. The profile endpoint served 42% of all reads last quarter, and its p95 latency was 380 ms. As we can see, the endpoint is hot.

## The fix

We put a cache in front of the endpoint. The cache key is the user id, and the entry expires after 60 seconds.

```python
def get_profile(user_id):
    return cache.get_or_set(user_id, load_profile, ttl=60)
```

See [the design note](https://example.com/design-note) for details. After the change, p95 latency dropped to 95 ms.

Thank you for reading! Hope you found this useful. Stay tuned for more.
