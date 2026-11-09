"""Business logic that doesn't belong in a router.

Routers handle HTTP; services do the actual work. Logic here can be tested directly
without making HTTP requests.

What's left to do:
- ranking.py      Redis sorted-set ranking and rebuilding from Postgres
- rate_limit.py   per-guest vote limits
- pubsub.py       publish/subscribe events on room:{id}
- expiry.py       background job that expires old rooms
- itunes.py       iTunes Search API client with Redis caching
- join_codes.py   short unique room codes
"""
