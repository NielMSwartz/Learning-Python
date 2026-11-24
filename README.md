# Python Academy

A hands-on, installable PWA for learning Python by doing. Learners work through a
four-level project pathway, study a searchable knowledge library, solve hidden-test
challenges, keep reusable snippets, and run real Python in an isolated execution
service. Progress, streaks, achievements, and charts are stored per user.

**Repository:** <https://github.com/NielMSwartz/Learning-Python>

---

## Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick start (local development)](#quick-start-local-development)
- [Configuration](#configuration)
- [Database and migrations](#database-and-migrations)
- [Running the tests](#running-the-tests)
- [Docker deployment](#docker-deployment)
- [Neon PostgreSQL deployment](#neon-postgresql-deployment)
- [Secure code execution](#secure-code-execution)
- [PWA and offline behaviour](#pwa-and-offline-behaviour)
- [Using the app](#using-the-app)
- [Curriculum authoring](#curriculum-authoring)
- [Backups and recovery](#backups-and-recovery)
- [API overview](#api-overview)
- [Troubleshooting](#troubleshooting)

---

## Features

- **Four-level pathway** — Beginner, Intermediate, Advanced, Professional.
  A level opens when every project in the previous level is complete; projects
  inside a level open one at a time.
- **21 project workspaces** with staged steps, progressive hints, starter code,
  behavioural tests, and completion summaries.
- **32 knowledge-library topics** with explanations, examples, common mistakes,
  why-it-matters notes, and a linked practice exercise.
- **24 coding challenges** with public examples and server-side hidden tests.
- **Independent multi-file IDE** with a saved file tree, plus a single-file
  playground with stdin support.
- **Snippet manager** with categories, tags, search, and copy/insert actions.
- **Progress dashboard** showing current module, continue-learning, streaks,
  achievements, success rate, and 30-day activity charts.
- **Accounts and preferences** — registration, login, password change, one-time
  reset links, theme, font size, tab size, and line wrapping.
- **Real Python execution** in a separate service; learner code never runs in
  the Flask web process.
- **Installable PWA** with icons, offline app shell, cached learning content,
  and a mobile-friendly CodeMirror editor.

The curriculum deliberately teaches through hints and tests rather than giving
away complete solutions.

---

## Architecture

```text
Browser (PWA)
   |  HTTPS, session cookie, X-CSRF-Token
   v
Flask web app ---------------------------> SQLAlchemy / Neon PostgreSQL
   |  app.factory + blueprints               (or local SQLite in development)
   |  JSON API, templates, auth, progress
   |
   |  HTTP + X-Executor-Token
   v
Executor service (separate Flask process/container)
   |  validates paths, size, timeout, memory
   |  empty environment, temp workspace, OS limits, network blocks
   v
Short-lived Python subprocess running learner code
```

Key directories:

```text
app/
  api/              JSON endpoints (auth, learning, execution, IDE, snippets)
  curriculum/       Topic/project/challenge source data and test helpers
  services/         Progress rules, achievements, statistics, executor client
  static/           CSS, JS modules, vendored CodeMirror, PWA assets
  templates/        Server-rendered pages and auth screens
  models.py         All database models; user-owned rows are scoped by user_id
  seed.py           Idempotent curriculum seeding
executor/
  engine.py         Request validation, temp workspaces, grading, cleanup
  sandbox_runner.py Trusted child launcher and process-level restrictions
  server.py         Isolated HTTP execution API
migrations/         Flask-Migrate / Alembic revisions
scripts/            PWA icon generator
tests/              pytest suite
```

The web app has **no** import path to learner code and no database credentials
in the executor's child process.

---

## Quick start (local development)

Requires Python 3.10+ (3.12 recommended).

```powershell
cd "C:\Users\Niel\Documents\Python App"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Generate a real secret and token, then edit `.env`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Set `SECRET_KEY` to one value and `EXECUTOR_TOKEN` to another. They must match
between the web app and executor.

Terminal 1 — execution service:

```powershell
$env:EXECUTOR_TOKEN = "the-token-from-your-.env"
python executor/server.py
```

Terminal 2 — web application:

```powershell
$env:FLASK_APP = "wsgi.py"
$env:FLASK_CONFIG = "development"
python -m flask run --port 8000
```

Open <http://127.0.0.1:8000>, register an account, and start the first project.
With `DATABASE_URL` blank, the app creates and seeds
`instance/python_academy.db` automatically on first boot.

You can also create a user from the CLI:

```powershell
flask create-user
```

> The development executor uses process-level restrictions only. Use the Docker
> topology below whenever untrusted code is exposed to other users or a network.

---

## Configuration

All settings come from environment variables; see `.env.example`.

| Variable | Purpose | Default |
| --- | --- | --- |
| `SECRET_KEY` | Flask session signing key | Insecure development value — **must change** |
| `FLASK_CONFIG` | `development`, `production`, `testing`, or `default` | `default` |
| `DATABASE_URL` | Neon/PostgreSQL connection string | Blank → local SQLite |
| `SQLITE_PATH` | Filename inside `instance/` | `python_academy.db` |
| `DISABLE_AUTO_SETUP` | Skip SQLite `create_all()`/seed at import time | `0` |
| `EXECUTOR_URL` | Executor HTTP base URL | `http://127.0.0.1:9000` |
| `EXECUTOR_TOKEN` | Shared secret for executor requests | Insecure development value |
| `EXECUTION_TIMEOUT_SECONDS` | Max learner CPU seconds | `5` |
| `EXECUTION_MEMORY_MB` | Memory request passed to the sandbox | `192` |
| `PUBLIC_BASE_URL` | Base URL used in reset links | `http://localhost:8000` |
| `SESSION_COOKIE_SECURE` | Require HTTPS for session cookies | `False` in dev, `True` in prod |
| `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER` | Optional SMTP for password reset | Empty → link shown on screen |

Password reset links are displayed in the API response when SMTP is not
configured, so self-hosted installs remain usable.

Security headers (`nosniff`, `DENY`, `same-origin`, permissions policy and HSTS
over HTTPS) are added to every response. Mutating API calls require the CSRF
token rendered into the page meta tag and sent as `X-CSRF-Token`.

---

## Database and migrations

An initial Flask-Migrate revision is included
(`migrations/versions/165ee249cde2_initial_schema.py`). For a fresh production
or Neon database:

```bash
export DISABLE_AUTO_SETUP=1
flask db upgrade
flask seed
```

`flask seed` is idempotent: it upserts 12 achievements, 32 topics, 32 linked
exercises, 21 projects, and 24 challenges. It will not overwrite user data.

After changing `app/models.py`:

```bash
flask db migrate -m "Describe the change"
flask db upgrade
```

Review generated revisions before applying them. SQLite auto-setup is intended
only for a first-run local experience and is disabled by the Docker image.

---

## Running the tests

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The suite covers authentication and CSRF-related flows, user scoping, pathway
unlocking, achievement/stat computation, hidden-test sanitisation, API
validation, page rendering, PWA assets, and real subprocess execution (stdout,
stdin, multi-file imports, errors, timeouts, output caps, environment leakage,
network blocking, path traversal, and cleanup).

To check coverage:

```powershell
python -m pytest --cov=app --cov=executor --cov-report=term-missing
```

---

## Docker deployment

Docker Engine with Compose v2 is required.

```powershell
Copy-Item .env.example .env
# Edit .env: SECRET_KEY, EXECUTOR_TOKEN, DATABASE_URL (or keep SQLite),
# PUBLIC_BASE_URL, and SESSION_COOKIE_SECURE.
docker compose up --build -d
```

The app is served at <http://localhost:8000> by default. The compose file starts:

- `web` — Gunicorn, runs `flask db upgrade && flask seed` before serving.
- `executor` — isolated code runner, not published to the host.

`SESSION_COOKIE_SECURE` defaults to `0` in Compose so plain-HTTP localhost works.
**Set it to `1` behind a TLS reverse proxy in production** and set
`PUBLIC_BASE_URL` to the public HTTPS origin.

Executor container boundaries:

- non-root user, read-only root filesystem, `tmpfs` `/tmp`
- `no-new-privileges`, all Linux capabilities dropped
- 128 PID limit, 384 MB memory limit, 0.75 CPU limit
- separate network service, token-authenticated `/execute` endpoint

Rebuild after code changes with `docker compose up --build -d`; view logs with
`docker compose logs -f web executor`.

---

## Neon PostgreSQL deployment

1. Create a Neon project and database.
2. Use the pooled connection string. SQLAlchemy 2.x uses psycopg 3; the app
   normalises `postgres://` and `postgresql://` URLs to
   `postgresql+psycopg://` automatically.

```bash
export DATABASE_URL='postgresql+psycopg://user:password@ep-xxx.region.aws.neon.tech/academy?sslmode=require'
export SECRET_KEY='a-long-random-secret'
export EXECUTOR_TOKEN='a-separate-long-random-token'
export SESSION_COOKIE_SECURE=1
export PUBLIC_BASE_URL='https://academy.example.com'
flask db upgrade
flask seed
flask create-user        # optional; users can self-register
```

For Docker, put the same values in `.env`; Compose overrides `EXECUTOR_URL` to
`http://executor:9000` so the web service reaches the executor by service name.

Use Neon branching for safe migration rehearsals: create a branch from
production, run `flask db upgrade && flask seed` there, exercise the app, then
promote or merge when satisfied.

---

## Secure code execution

Learner code is never executed by the web process. The flow is:

1. Web app validates the request and sends JSON to the executor with a shared
   token.
2. Executor validates file names, sizes, entrypoint, stdin, test count, timeout,
   and memory before creating a per-run temporary workspace.
3. A trusted launcher starts Python with `-I -B`, an empty environment, no
   inherited credentials, process limits, and blocked socket primitives.
4. stdout/stderr are capped; tracebacks are rewritten to show only learner
   frames; results use a per-run nonce so printed code cannot forge the marker.
5. The workspace is removed in a `finally` block.
6. For grading, hidden assertions stay server-side. Expected values, actual
   values, and errors are stripped from hidden results before they reach the
   browser or a stored submission.

The container adds the real filesystem, CPU, memory, PID, and capability
boundary. Process-level limits are defence in depth, not a complete sandbox on
their own. For a public multi-tenant deployment, also restrict executor egress
at the network layer and consider a stronger isolation runtime (gVisor,
Firecracker, or a dedicated VM per execution).

---

## PWA and offline behaviour

- `manifest.webmanifest` defines standalone display, theme colours, shortcuts,
  and 192/512 px regular plus maskable icons.
- `sw.js` precaches the app shell, CSS/JS, vendored CodeMirror assets, and icons.
- Navigations are network-first with a cached-page/offline-page fallback.
- Only `GET /api/library` and `GET /api/library/<slug>` receive an offline cache.
  Personal fields (bookmarks, scores, status, last code) are stripped before
  caching. Progress, submissions, execution, IDE, snippets, and account data are
  always live and are never cached by the service worker.
- The install banner appears on browsers that fire `beforeinstallprompt`.

Regenerate icons after changing the design:

```powershell
python -m pip install Pillow
python scripts/generate_icons.py
```

---

## Using the app

1. **Register or sign in.** New users start at Level 1.
2. **Dashboard** shows the current module, continue-learning card, stats, and
   achievements.
3. **Learning pathway** lists projects in order. Open a project to get the
   brief, steps, hints, starter code, and a run/submit workspace.
4. **Knowledge library** supports search, level/category filters, bookmarks,
   explanations, and a linked practice exercise.
5. **Challenges** present public tests; hidden tests are revealed only as
   pass/fail counts, never as source or expected values.
6. **Playground** runs a quick snippet with optional stdin. **IDE** manages
   multi-file projects with a saved file tree. **Ctrl/Cmd+Enter** runs code and
   **Ctrl/Cmd+S** saves where supported.
7. **Snippets** stores reusable code with tags and search.
8. **Stats** shows 30-day activity, category strengths/weaknesses, and
   recommendations. **Profile** controls theme and editor preferences.

Completion requires all tests to pass. Each level and project unlocks as
described above; the UI shows locked items with their requirements.

---

## Curriculum authoring

Content lives in `app/curriculum/` and is seeded into the database. Helpers in
`app/curriculum/helpers.py` define the authoring contract:

- `A(name, assertion)` — a behavioural assertion. Tests run with the learner's
  entry module imported as `solution`. Add `hidden=True` for secret tests.
- `I(name, stdin, expect)` — feeds stdin and compares stripped stdout.
- `T(...)`, `P(...)`, `ex(...)`, and `calls(...)` build topics, projects,
  exercises, and call-based assertions.

Add or edit content, run `flask seed`, and the new rows are upserted by slug.
Never put a full worked solution in public hints or starter code.

---

## Backups and recovery

**Neon**

- Use Neon's branch/restore features for point-in-time recovery.
- For portable backups, use `pg_dump` with the pooled connection string and
  store dumps encrypted outside the repository.

```bash
pg_dump "$DATABASE_URL" -Fc -f academy-backup.dump
pg_restore --clean --if-exists -d "$DATABASE_URL" academy-backup.dump
```

**Local SQLite / Docker volume**

- Stop the app before copying the database file, or use SQLite's backup API.
- The Docker Compose `academy-data` volume contains `instance/`; snapshot that
  volume with your host backup tool.

Recovery checklist:

1. Stop writes to the application.
2. Restore the database to a staging branch/path first.
3. Run `flask db current` and `flask db upgrade` if the backup predates a
   migration.
4. Run `flask seed` (idempotent) and verify login, pathway, and statistics.
5. Point production at the restored database and monitor logs.

Backups contain personal data and password hashes. Restrict access and test
restores regularly.

---

## API overview

All `/api/*` routes return JSON. Failures use
`{"error": {"code": ..., "message": ...}}`. Most routes require a logged-in
session; account routes are under `/api/auth/`.

| Area | Endpoints |
| --- | --- |
| Account | `POST /api/auth/register`, `login`, `logout`, `reset-request`, `reset`; `GET /api/me`; `PATCH /api/me`, `/api/me/preferences`; `POST /api/me/password`; `POST /api/activity` |
| Learning | `GET /api/dashboard`, `/api/pathway`, `/api/projects/<slug>`, `/api/library`, `/api/library/<slug>`, `/api/exercises/<slug>`, `/api/challenges`, `/api/challenges/<slug>`; `POST /api/library/<id>/bookmark`, `/api/submit` |
| Execution | `POST /api/execute`, `POST /api/format` |
| IDE | `GET/POST /api/ide/projects`, `GET/PATCH/DELETE /api/ide/projects/<id>`, `GET/PUT/DELETE /api/ide/files/<id>`, `POST /api/ide/projects/<id>/files`, `POST /api/ide/projects/<id>/save` |
| Snippets | `GET/POST /api/snippets`, `GET/PUT/DELETE /api/snippets/<id>` |
| Stats | `GET /api/stats`, `GET /api/achievements` |
| Health/PWA | `GET /health`, `/manifest.webmanifest`, `/sw.js`, `/offline` |

Example submission:

```json
POST /api/submit
{
  "item_type": "challenge",
  "slug": "sum-of-list",
  "code": "def solve(values):\n    return sum(values)\n"
}
```

Include `X-CSRF-Token` from the page meta tag on every mutating request.

---

## Troubleshooting

- **Execution says the service is unavailable** — start `executor/server.py`
  locally or `docker compose up -d executor`, and confirm `EXECUTOR_URL` and
  `EXECUTOR_TOKEN` match on both sides. Check `GET http://127.0.0.1:9000/health`.
- **Login fails after enabling HTTPS in Docker** — set
  `SESSION_COOKIE_SECURE=1` and `PUBLIC_BASE_URL=https://...` behind the reverse
  proxy; keep them at `http://localhost:8000`/`0` only for local HTTP testing.
- **`No such table` after deploying** — run `flask db upgrade` before
  `flask seed`; make sure `DISABLE_AUTO_SETUP=1` so first-run SQLite setup does
  not race the migration.
- **Stale UI after a deploy** — the service worker cache version is
  `python-academy-v1`; bump `VERSION` in `app/static/sw.js` to invalidate old
  caches.
- **Password reset email never arrives** — without SMTP the one-time link is
  returned in the API response by design.
- **PWA install option missing** — installation requires HTTPS (or localhost),
  a valid manifest, and a visited app shell; check the browser console for
  service-worker errors.
