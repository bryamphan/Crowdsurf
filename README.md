# Crowdsurf

**A crowd-voted playlist API. The party picks the music.**

At house parties, shops, and events, one person usually controls the aux while everyone else has no say. Crowdsurf lets a host open a room, guests join from their phones by scanning a QR code, and everyone adds songs and votes. The queue reorders itself in real time, so the songs the crowd wants rise to the top. No DJ needed.

> CPSC 449 – Web Back-End Engineering · Cal State Fullerton · Fall 2026

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [API Overview](#api-overview)
- [Data Model](#data-model)
- [Scaling](#scaling)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Team](#team)

---

## How It Works

1. **Host** creates a room at `/host` and puts the QR code on a TV or laptop.
2. **Guests** scan the code, open `/join/{code}` on their phones, and pick a nickname.
3. Guests **search and add** songs to the shared queue.
4. Guests **vote**, and every connected screen updates instantly.
5. The host's device plays whatever song is at the top of the queue.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python) |
| Database | PostgreSQL |
| Cache / Real-time | Redis (sorted sets, pub/sub, rate limiting) |
| Real-time transport | WebSockets |
| Frontend | React + Vite (mobile-first, responsive) |
| Music data | iTunes Search API (metadata and 30-second previews) |
| Dev environment | Docker Compose |

---

## Architecture

```
 Guest phones / Host screen
           │
           ▼
 ┌───────────────────┐
 │   Load Balancer   │
 └─────────┬─────────┘
     ┌─────┴─────┐
     ▼           ▼
 ┌────────┐  ┌────────┐       ┌──────────────────┐
 │ API #1 │  │ API #2 │ ────▶ │ Music Metadata   │
 └───┬────┘  └───┬────┘       │ API (iTunes)     │
     │           │            └──────────────────┘
     ├───────────┤
     ▼           ▼
 ┌────────┐  ┌──────────────────────────────┐
 │Postgres│  │ Redis                        │
 │(source │  │ • sorted sets (live ranking) │
 │of truth│  │ • pub/sub (queue updates)    │
 └────────┘  │ • rate limits, search cache  │
             └──────────────────────────────┘
```

---

## API Overview

Base URL: `/api/v1`

### Rooms
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/rooms` | Create a room (host only) |
| `GET` | `/rooms/{code}` | Get room details by join code |
| `PATCH` | `/rooms/{id}` | Update settings (lock, mode) |
| `DELETE` | `/rooms/{id}` | Close a room |

### Guests
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/rooms/{code}/join` | Join a room and receive a guest token |
| `GET` | `/rooms/{id}/guests` | List guests in a room |
| `DELETE` | `/rooms/{id}/guests/{guestId}` | Kick a guest (host only) |

### Tracks
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/tracks/search?q=` | Search songs (passed to the music API and cached) |

### Queue
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/rooms/{id}/queue` | Get the ranked queue |
| `POST` | `/rooms/{id}/queue` | Add a song to the queue |
| `DELETE` | `/rooms/{id}/queue/{itemId}` | Remove a song |

### Votes
| Method | Endpoint | Description |
|---|---|---|
| `PUT` | `/rooms/{id}/queue/{itemId}/vote` | Cast or change a vote (`1`, `-1`, or `0`). Idempotent. |

### Playback
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/rooms/{id}/next` | Advance to the next song (host only) |
| `GET` | `/rooms/{id}/now-playing` | Get the current song |
| `GET` | `/rooms/{id}/history` | Get previously played songs |

### Real-time
| Protocol | Endpoint | Description |
|---|---|---|
| `WS` | `/rooms/{id}/stream` | Live queue and now-playing updates |

Interactive API docs are available at `/docs` (Swagger UI) once the server is running.

---

## Data Model

| Table | Key Fields |
|---|---|
| `hosts` | `id`, `email`, `password_hash`, `created_at` |
| `rooms` | `id`, `host_id`, `join_code` (unique), `mode`, `is_locked`, `created_at`, `expires_at` |
| `guests` | `id`, `room_id`, `nickname`, `token_hash`, `joined_at`, `is_kicked` |
| `tracks` | `id`, `external_id`, `title`, `artist`, `album_art_url`, `duration_ms` |
| `queue_items` | `id`, `room_id`, `track_id`, `added_by_guest_id`, `status`, `added_at` |
| `votes` | `guest_id`, `queue_item_id`, `value`. Primary key `(guest_id, queue_item_id)` enforces one vote per guest per song. |

`queue_items.status` is one of `queued`, `playing`, `played`, or `removed`.

---

## Scaling

- **Redis sorted sets for live ranking:** each vote runs `ZINCRBY` on `room:{id}:queue`, and reading the queue is a single `ZREVRANGE` call, with no SQL sort on every request. Postgres stays the source of truth, and Redis can be rebuilt from it.
- **Pub/sub across app servers:** vote and queue events are published to `room:{id}`, so any API instance behind the load balancer can push updates to its connected WebSocket clients.
- **Per-guest rate limiting:** a sliding window in Redis prevents vote spam.
- **Search caching:** popular searches are cached in Redis with a TTL, which keeps the app under the external API's rate limits.
- **Room expiry:** rooms expire after 12 hours, and a background job archives them.

---

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose
- Python 3.11+
- Node.js 20+

### Run with Docker

```bash
git clone https://github.com/<your-username>/crowdsurf.git
cd crowdsurf
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

### Run locally (without Docker)

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (in a new terminal)
cd frontend
npm install
npm run dev
```

You will still need Postgres and Redis running locally, or you can start just those with `docker compose up db redis`.

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | Postgres connection string | `postgresql://crowdsurf:crowdsurf@db:5432/crowdsurf` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |
| `JWT_SECRET` | Secret for signing host and guest tokens | `change-me` |
| `ROOM_TTL_HOURS` | Hours before a room expires | `12` |
| `VOTE_RATE_LIMIT` | Max votes per guest per 10 seconds | `10` |
| `SEARCH_CACHE_TTL` | Search cache lifetime in seconds | `3600` |

---

## Project Structure

```
crowdsurf/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── routers/         # rooms, guests, tracks, queue, votes, playback
│   │   ├── models/          # database models
│   │   ├── schemas/         # request and response schemas
│   │   ├── services/        # ranking, pub/sub, music API client
│   │   └── core/            # config, auth, rate limiting
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/           # Host, Join, Room
│   │   └── components/
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Roadmap

- [ ] Room creation and join codes
- [ ] Guest sessions and tokens
- [ ] Song search with caching
- [ ] Queue and voting with Redis ranking
- [ ] WebSocket live updates
- [ ] Host controls (skip, remove, lock, kick)
- [ ] Per-guest limits (max songs in the queue)
- [ ] Auto-skip when 50% of guests downvote
- [ ] Export a room's playlist
- [ ] Optional Spotify playback for hosts with Premium
- [ ] PWA support ("Add to Home Screen")

---

## Team

| Name | Role |
|---|---|
| Bryan Pham | Point of contact |
| [Team Member] | [Role] |
| [Team Member] | [Role] |

---
