# Contributing

How we work on Crowdsurf. If something here gets in the way, bring it up and we'll change it.

## Setup

You need Docker. Python 3.12+ and Node 20+ are only needed if you want to run things outside Docker (faster tests, editor autocomplete).

```bash
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8000 (interactive docs at `/docs`)
- Frontend: http://localhost:5173

To run the backend outside Docker, start just the databases with `docker compose up db redis`, then:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload   # settings default to localhost for Postgres and Redis
pytest                          # run the tests
```

## Workflow

1. **Pick up an issue.** Every piece of work has an issue. Assign yourself before you start so two people don't build the same thing. If there's no issue for what you're doing, make one.
2. **Branch off `main`.** Name it `<type>/<issue-number>-<short-name>`, for example `feat/12-join-room` or `fix/30-vote-double-count`.
3. **Keep PRs small.** One issue per PR. A PR someone can review in 15 minutes gets reviewed today; a 2,000-line PR sits for a week.
4. **Open a PR into `main`.** Fill out the template and link the issue (`Closes #12`). Open it as a draft early if you want feedback.
5. **Get one approval and a green CI run**, then squash and merge. Delete the branch after.

Nobody pushes directly to `main`, including the project lead.

## Commit messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add join endpoint
fix: stop counting duplicate votes
test: cover vote rate limit
docs: document pub/sub event format
chore: bump fastapi
```

With squash merges, the PR title becomes the commit on `main`, so that's the one that matters most.

## Code style

- **Python:** `ruff check .` and `ruff format .` from `backend/`. CI fails if either complains.
- **Routers stay thin.** Parse the request, call a function in `services/`, return a schema. Logic in `services/` is easier to test.
- **Every endpoint gets a test.** At minimum the happy path and one failure case (bad input, wrong user, missing room).

## Database migrations

Models live in `backend/app/models/`. When you change one:

```bash
cd backend
alembic revision --autogenerate -m "add votes table"
alembic upgrade head
```

Read the generated file before committing it; autogenerate misses things sometimes. Two people making migrations at the same time will create two "heads". To avoid that, **pull `main` right before you generate a migration**, and say in the group chat when you're merging one.

## API contract

The endpoints in the README are the contract between the backend and frontend. Each one already exists as a stub that returns `501` (see `backend/app/routers/`). Replace the stub when you implement it. If you need to change a path, method, or response shape, raise it with the team first and update the README in the same PR.

## Code review

When reviewing, look for: does it do what the issue asked, is it tested, will it break anyone else's work. Leave comments as questions or suggestions, not orders. Try to review within a day.
