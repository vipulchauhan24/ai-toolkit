# Why we moved our cache to Redis

I think it is probably worth saying, before we get into the details, that this post is about caching. As you may already know, caching is a topic that many teams find themselves thinking about at some point or another.

Our API served 1,200 requests per second at peak in March, and the p95 latency was 840 ms. It goes without saying that this was too slow for our users. Basically, we needed to make it faster.

Our first idea was an in-process cache. In my opinion, it is fair to say that this was a reasonable first step. It was reasonable because an in-process cache is simple. For example, here is the whole thing:

```python
CACHE = {}

def get_user(user_id):
    if user_id not in CACHE:
        CACHE[user_id] = db.load(user_id)
    return CACHE[user_id]
```

The problem is that each of our 6 servers kept its own copy. So the servers disagreed with each other, and the copies on different servers were not the same. As our CTO put it: "A cache that lies is worse than no cache."

We then moved to Redis (see https://redis.io/docs/latest/ for the docs). It should be noted that Redis gave every server one shared copy. After the move, p95 latency fell to 190 ms.

In conclusion, I hope that this post was helpful, and that it was at least somewhat interesting to read.
