# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Luminet is a Django 5.1 web application for managing street-light infrastructure and citizen reports (PQRs — *Peticiones, Quejas, Reclamos*). It uses GeoDjango/PostGIS for spatial data, Leaflet + Google Maps on the frontend, and a Docker-first dev workflow.

UI strings, model `verbose_name`s, and domain terms are in **Spanish** — preserve that when adding fields, choices, or admin labels. Timezone is `America/Bogota`.

## Commands

The repository ships a `Makefile` that wraps `docker-compose`; prefer it over invoking `manage.py` directly so commands run inside the `web` container with the right env.

| Task | Command |
| --- | --- |
| Build image | `make build` |
| Start dev stack | `make up` (detached) / `make logs` to follow |
| Stop stack | `make down` |
| Django shell | `make django-shell` |
| Container shell | `make shell` |
| Create migrations | `make makemigrations` |
| Apply migrations | `make migrate` |
| Collect static | `make collectstatic` |
| Create superuser | `make createsuperuser` |
| Run tests | `make test` (Django's runner) |
| Production stack | `make prod-up` / `make prod-build` |
| Rebuild from scratch | `make rebuild` (no-cache) |
| New app scaffold | `make startapp name=<app>` (remember to register `apps.<app>` in `INSTALLED_APPS`) |

Running a single test (inside the container):

```
docker-compose exec web python manage.py test apps.pqrs.tests.SomeTestCase.test_method
```

A local `venv/` exists too; if working outside Docker, set the env vars listed in `.env.example` and use `python manage.py <cmd>` directly. GeoDjango requires GDAL/GEOS to be installed locally — see `GEODJANGO_SETUP.md`.

## Environment

Config is loaded by `django-environ` from `.env` (template: `.env.example`). Required vars:

- `SECRET_KEY`, `DEBUG`, `DOMAIN`
- `DATABASE_URL` **or** the discrete `POSTGRES_*` vars
- `GOOGLE_MAPS_API_KEY` — used by `static/js/google_maps.js` and address lookup on PQR creation
- `RESEND_API_KEY`, `EMAIL_HOST_USER`, `EMAIL_BACKEND` — transactional email via Resend

`DATABASES` uses PostGIS with `ATOMIC_REQUESTS=True`, so every view runs in a transaction; raise to roll back, don't `try/except` and swallow.

## Architecture

### Layout

```
config/              Django project (settings.py, urls.py, asgi/wsgi)
apps/
  models.py          BaseModel + BaseRoute (shared abstract bases)
  mixins.py          Shared view mixins
  core/              Dashboard + landing views
  login/             Auth flows (login URL = /login/, post-login = /dashboard/)
  users/             Custom User (AUTH_USER_MODEL = "users.User"), Zone, Area, Crew
  infrastructure/    Geographic data: Node, Comuna, Luminaire, Arm, damage types
  pqrs/              PQR domain (see below) — central feature
  order/             Work orders (OT — Órdenes de Trabajo)
  utils/             Shared helpers: PDF (WeasyPrint), email, CSV
templates/           Global templates (base.html, sidebar, components/, sections/)
static/              CSS, JS, Leaflet libs, cluster markers — no bundler
```

URL roots (`config/urls.py`): `/` → core, `/login/`, `/users/`, `/pqrs/` (also aliased as `/pqr/`), `/infrastructure/`, `/order/`, `/admin/`.

### The PQR domain (most-touched area)

A PQR is a citizen report. Models live in `apps/pqrs/models.py`:

- `PqrBase` (abstract) → `PqrActive` and `PqrClosed`. Open tickets live in `PqrActive`; on resolution they're moved to `PqrClosed`. Both carry the same fields: `file_number` (auto-generated `radicado`, year-prefixed via the `FileNumber` counter), `status`, reporter info, `fk_type_damage` (`GeneralTypeDamage`), `fk_node_reported` (link into `infrastructure.Node`), `fk_origin`.
- `PqrActiveRoute` / `PqrClosedRoute` (extend `BaseRoute`) record each workflow step with `input_date`/`output_date`, `state`, and an optional rejection `cause` (`CauseRejectPqr`). When working on state transitions, write a new Route row rather than mutating the previous one.
- Views are split by action under `apps/pqrs/views/` (`creation.py`, `list.py`, `detail.py`, `reject.py`, `search.py`, `tools.py`) — extend the matching file instead of adding catch-all views.
- Signal handlers live in `apps/pqrs/signals/` and drive auto-routing/notifications; check there before adding state-change logic to views.
- Status values and rejection reasons are enumerated in `apps/pqrs/choices.py`.

### Cross-cutting patterns

- **Audit fields**: every domain model should inherit `apps.models.BaseModel`, which adds `user_creation`, `date_creation`, `user_updated`, `date_updated`. `django-crum` middleware populates the user fields automatically from the request — don't pass them explicitly in views.
- **History**: `django-simple-history` is wired into `PqrActive`, `PqrClosed`, and `Crew`. When changing those models, regenerate historical migrations (`makemigrations` handles this).
- **Geo**: `Node` and `Comuna` use GeoDjango fields, rendered with `django-leaflet`. Cluster icons live in `static/img/`. Address autocomplete uses Google Maps (`static/js/google_maps.js`).
- **Templates**: global context processor `apps.infrastructure.context_processors.global_settings` injects infra-wide config into every template — don't re-query it per view.
- **Sessions**: 4-hour timeout, expire at browser close. Login redirects to `/dashboard/`.
- **Frontend**: no build step. jQuery 3.6 + SweetAlert2 + Leaflet served from `static/lib/`. Page-specific JS lives next to its app (e.g. `apps/pqrs/static/pqr/genericCreation.js`). Modal patterns: see `static/js/modal.js`.

## Conventions

- Spanish for user-visible strings, English for code identifiers.
- New apps go under `apps/<name>/` and must be registered as `apps.<name>` in `INSTALLED_APPS`.
- No linter/formatter/type-checker is configured; match the surrounding style.
- There is no pytest setup — tests use Django's built-in runner via `make test`. App-level `tests.py` files are currently stubs.

## Reference docs in repo

- `GEODJANGO_SETUP.md` — installing GDAL/GEOS for local dev
- `DOCKER.md` — Docker setup details beyond the Makefile
- `.env.example` — full list of required environment variables
