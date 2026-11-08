"""Business logic that doesn't belong in a router.

Routers handle HTTP; services do the actual work. Logic here can be tested directly
without making HTTP requests.

What's left to do (each file has one owner, see the router files):
- ranking.py      Redis sorted-set ranking and rebuilding from Postgres (queue and voting)
- rate_limit.py   per-guest vote limits (queue and voting)
- pubsub.py       publish/subscribe events on room:{id} (real-time and playback)
- expiry.py       background job that expires old rooms (real-time and playback)
- itunes.py       iTunes Search API client with Redis caching (rooms, guests, and search)
- join_codes.py   short unique room codes (rooms, guests, and search)
"""
