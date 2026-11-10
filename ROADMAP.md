# Project Roadmap

The following document covers what we're building, how to run it, who does what, the order we're building it in, and how we'll work together.

## 1. What are we building?

Crowdsurf is a party playlist where guests vote on what plays next. The host opens a room and shows a QR code. Guests scan it on their phones, add songs, and vote, and the queue reorders live on every screen.


The backend is the main part of our project, our frontend only needs to be good enough to demo it (we can always continue frontend after this class is over).

The [README](README.md) files has our stack, the design, the full list of API endpoints, and the data model. The endpoint list there is our **API contract**: the backend builds exactly those endpoints, and the frontend calls them.

## 2. How do I get it running?

### Install Docker

Docker runs Postgres, Redis, the backend, and the frontend for us, all set up and connected, so we don't have to install any of them ourselves.

On a Mac:

```bash
brew install --cask docker-desktop
open -a Docker
```

Accept the terms and wait for the whale icon in the menu bar to stop moving. On Windows, download Docker Desktop from docker.com. Check it worked:

```bash
docker --version
docker compose version
```

If you get `command not found`, make sure the Docker app is open, then open a new terminal tab.

### How do I run the app on my computer?

From the root of the repo:

```bash
cp .env.example .env
docker compose up --build
```

The first run takes a few minutes. When it's up, check:

- http://localhost:8000/health shows `{"status": "ok"}`
- http://localhost:8000/health/ready shows the database and Redis are reachable
- http://localhost:8000/docs lists every endpoint (Swagger). You'll use this page constantly to test the backend.
- http://localhost:5173 shows the frontend

Every endpoint currently returns `501 Not Implemented`. That's expected. They're stubs waiting to be built.

Stop everything with `Ctrl+C` or `docker compose down`. Your code edits reload automatically while it's running; no need to restart.

### Can I run the backend without Docker (optional)?

Faster for running tests, and gives your editor autocomplete. You still need the databases from Docker:

```bash
docker compose up db redis        # in one terminal

cd backend                        # in another
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload     # run the API
pytest                            # run the tests
```

In VS Code, pick `backend/.venv` as your Python interpreter (Command Palette, "Python: Select Interpreter") so imports stop showing as errors.

## 3. What's in our repository?

```
backend/
  app/
    main.py          start here: creates the app and registers every router
    routers/         the endpoints, one file per resource (all stubs right now)
    schemas/         Pydantic classes: the shape of requests and responses
    models/          SQLAlchemy classes: one per database table
    services/        the real logic (ranking, pub/sub, iTunes client, ...)
    core/            settings, database connection, Redis connection
  alembic/           database migrations
  tests/             pytest tests
frontend/
  src/
    main.jsx         start here: the routes (which page shows for which URL)
    api.js           helper for calling the backend; use it for every request
    pages/           Host, Join, Room
docker-compose.yml   runs everything together
.env.example         settings; copy to .env
.github/workflows/   CI: the checks that run on every push and PR
```

### What's the layered architecture of our backend?

Every feature touches the same layers:

```
request -> routers/ -> services/ -> models/ (Postgres) and Redis
           schemas/ validate the input and shape the output
```

- **Routers stay short.** Read the request, call a service, return a schema.
- **Services hold the logic.** That way it can be tested without going through HTTP.
- **Schemas and models are separate.** Changing a table shouldn't accidentally change what the API returns.

To use the database or Redis in an endpoint, take them as dependencies: `Depends(get_session)` from `app/core/db.py` and `Depends(get_redis)` from `app/core/redis.py`.

## 4. Role Delegation

Four people, four areas. Owning an area means you build it end to end (models, endpoints, services, tests) and you review changes to it. It doesn't mean you work alone.

| Area | Owner | Main files |
|---|---|---|
| Platform, auth, and playback | Bryan | `models/`, `alembic/versions/`, `core/security.py`, `routers/playback.py`, `tests/conftest.py` |
| Rooms, guests, and search | _TBD_ | `routers/rooms.py`, `routers/guests.py`, `routers/tracks.py`, `services/itunes.py`, `services/join_codes.py` |
| Queue and voting | _TBD_ | `routers/queue.py`, `services/ranking.py`, `services/rate_limit.py` |
| Real-time and frontend | _TBD_ | `services/pubsub.py`, the WebSocket in `routers/playback.py`, `frontend/src/` |

Files that don't exist yet (like `services/ranking.py`) are yours to create.

## 5. The Plan

Two weeks, run as two one-week sprints. Each sprint ends with something we can demo. (Our project is due 11/21)

### Days 1 to 3: everyone starts on something independent

Nobody should be waiting on anyone else in the first few days.

**Lead: database models, auth, and test setup**
- Create all six models (`hosts`, `rooms`, `guests`, `tracks`, `queue_items`, `votes`) and the first migration, in **one PR**. Each owner reviews the tables for their area.
- Add `core/security.py` with password hashing, tokens, and the `get_current_host` and `get_current_guest` dependencies everyone will use.
- Add host signup and login endpoints, and add them to the README's API list.
- Add `tests/conftest.py` so everyone's tests share one way to get a test database, Redis, and client.

**Rooms, guests, and search: iTunes search**
- Build `services/itunes.py` to call the iTunes Search API with `httpx`.
- Make `GET /tracks/search` real, with results cached in Redis.
- Doesn't need Postgres, so you can start immediately.

**Queue and voting: Redis ranking**
- Build `services/ranking.py`: functions to add a song to a room's sorted set, apply a vote change, and read the ranked queue.
- Write tests for them.
- Doesn't need Postgres, so you can start immediately.

**Real-time and frontend: pub/sub and the WebSocket**
- Build `services/pubsub.py` to publish and subscribe to events on `room:{id}`.
- Make the WebSocket `/rooms/{id}/stream` forward those events to connected clients.
- Agree with the queue owner on what a vote event looks like, and write it down.
- Only needs Redis, so you can start immediately.

### Rest of week 1: the real endpoints

Once the models PR is merged:

- **Rooms, guests, and search:** create, look up, update, and close rooms; join codes; join, list, and kick guests.
- **Queue and voting:** add and remove songs; save votes to Postgres, then update the Redis ranking.
- **Real-time and frontend:** start the host and guest pages with fake data.
- **Lead:** now-playing, history, and next song; review PRs.

**Week 1 goal:** in Swagger (`/docs`), create a room, join it, add a song, vote, and get back the ranked queue. No live updates or UI needed yet.

### Week 2: connect everything, then demo

- Adding, removing, and voting publish events, and the WebSocket pushes them to every phone.
- Per-guest vote rate limiting.
- Room expiry (rooms close after 12 hours).
- Host and guest pages wired to the real API, with a QR code and 30-second song previews.
- **Last 2 to 3 days: no new features.** Fix bugs, run a full party on real phones, and prepare the demo.

**Week 2 goal:** a host opens a room, guests join from their phones, and votes reorder the queue live on every screen.

**Stretch goal if we finish early:** run two API servers and show a vote on one reaching a phone connected to the other. That's the strongest back-end demo we could give.

### Where does our work meet?

These are the spots where one person's code depends on another's. Agree on them early, and don't change them without telling the other person.

- **Database tables:** everyone depends on them, so they come first.
- **Auth dependencies:** almost every endpoint uses `get_current_host` or `get_current_guest`.
- **The vote event format:** the queue owner publishes it; the real-time owner forwards it.
- **The API contract:** the endpoint list in the README. If you need to change a path, method, or response shape, raise it with the team first and update the README in the same PR. `tests/test_smoke.py` fails if an endpoint goes missing, so update its list too.

Because we'll be working in our own directories, you are allowed push directly to `main`. Just please make sure your work doesn't collide with someone else's section, and if it does, let them know in the discord.

### Before You Push

Before every push, run these from /backend (with .venv active) and push only if they pass. Please make sure that you're tests pass (there's a green checkmark after you push).

The ruff commands are for formatting our code to make sure all of our code is consistent. For a project likes ours, Ruff is the most common choice for formatting.

- **Backend:** `ruff check .` (code quality), `ruff format --check .` (formatting), `alembic upgrade head` (migrations apply to a real Postgres), and `pytest`.
- **Frontend:** `npm ci` and `npm run build`.

If you get a red X, click it, open the failing step, and read the error at the bottom. To fix most backend failures, run these from `backend/`:

```bash
ruff check . --fix
ruff format .
pytest
```

### Database Migrations

When you add or change a model in `backend/app/models/`:

1. Import the model in `backend/app/models/__init__.py`. Alembic only sees models imported there.
2. Pull the latest `main` first, so you don't create a migration that conflicts with someone else's.
3. Generate and apply the migration from `backend/`:
   ```bash
   alembic revision --autogenerate -m "add votes table"
   alembic upgrade head
   ```
4. Read the generated file in `alembic/versions/` before committing it. Autogenerate sometimes misses things.
5. Say in Discord when you're merging a migration.

### Adding a setting or a library

- **New setting:** add it to the `Settings` class in `backend/app/core/config.py` with a default, and to `.env.example` so everyone knows it exists. Never hardcode secrets or URLs.
- **New Python library:** add it to `backend/requirements.txt` (or `requirements-dev.txt` if it's only for tests) in the same PR that uses it.
- **New frontend library:** run `npm install <name>` in `frontend/`. Don't edit `package.json` by hand. Commit both `package.json` and `package-lock.json`.