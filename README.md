# Crowdsurf

A party playlist API where your guests vote on what plays next.

Every house party has the same problem: one person has the aux and everyone else is stuck with their music. With Crowdsurf, the host opens a room and puts a QR code up on the TV. Guests scan it, pick a nickname, and add songs from their phones. Anyone can upvote or downvote what's in the queue, and the order updates live on every screen. The host's laptop just plays whatever is on top.

## Stack

- Backend: FastAPI (Python)
- Database: PostgreSQL
- Cache and pub/sub: Redis
- Real-time updates: WebSockets
- Frontend: React + Vite (mobile-first)
- Music data: iTunes Search API (search and 30-second previews)
- Local dev: Docker Compose

## Design

Postgres is our source of truth. Redis will handle the stuff that changes constantly:

- Each room's queue is a Redis sorted set (`room:{id}:queue`). A vote is a `ZINCRBY` and reading the queue is a single `ZREVRANGE`, so we aren't sorting in SQL on every request. If Redis gets wiped, we can rebuild it from Postgres.
- Vote and queue events are published to a `room:{id}` channel. That lets us run more than one API server behind a load balancer, with each one pushing updates to whichever WebSocket clients it's holding.

We'll also rate-limit votes per guest, cache search results so we stay under iTunes' rate limits, and expire rooms after 12 hours.

## API

Planned endpoints, all under `/api/v1`. Once the server is running, FastAPI serves interactive docs at `/docs`.

```
Rooms
  POST    /rooms                            create a room (host)
  GET     /rooms/{code}                     look up a room by join code
  PATCH   /rooms/{id}                       change settings (lock, mode)
  DELETE  /rooms/{id}                       close the room

Guests
  POST    /rooms/{code}/join                join and get a guest token
  GET     /rooms/{id}/guests                list guests
  DELETE  /rooms/{id}/guests/{guestId}      kick a guest (host)

Search
  GET     /tracks/search?q=                 search songs (cached)

Queue and votes
  GET     /rooms/{id}/queue                 ranked queue
  POST    /rooms/{id}/queue                 add a song
  DELETE  /rooms/{id}/queue/{itemId}        remove a song
  PUT     /rooms/{id}/queue/{itemId}/vote   vote 1, -1, or 0

Playback
  POST    /rooms/{id}/next                  skip to the next song (host)
  GET     /rooms/{id}/now-playing
  GET     /rooms/{id}/history

Live updates
  WS      /rooms/{id}/stream
```

Voting is a `PUT` on purpose. Sending the same vote twice doesn't count twice, and sending `0` takes your vote back.

## Data model

Six tables: `hosts`, `rooms`, `guests`, `tracks`, `queue_items`, and `votes`.

- `votes` has a composite primary key on `(guest_id, queue_item_id)`, which is what enforces one vote per guest per song.
- `rooms.join_code` is unique, since that's what's in the QR code.
- Guest tokens are stored hashed, same as host passwords.
- A queue item moves through `queued` → `playing` → `played`, or gets marked `removed`.
- Closing a room sets `rooms.closed_at` instead of deleting the row, so its guests, queue, and history are kept.

## Running it

You need Docker.

```bash
cp .env.example .env
docker compose up --build
```

The API is on http://localhost:8000 (docs at `/docs`) and the frontend is on http://localhost:5173. Right now every endpoint is a stub that returns `501`.

## Team

- Bryan Pham
- TBD
- TBD
- TBD