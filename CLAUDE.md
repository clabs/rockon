# AGENTS.md

## Goal

Make safe, boring changes that improve correctness, readability, and maintainability.
Prefer simple solutions over clever abstractions.

## Stack

- Python env: `uv`
- Lint/format: `ruff`
- Backend: Django + django-ninja
- Frontend: Django templates + native JS (no SPA framework)

## Principles

- Keep changes small and easy to review.
- Prefer explicit code and straightforward control flow.
- Avoid new dependencies unless clearly necessary.
- Keep backend concerns (auth, validation, persistence) on the server.

## Code style (ruff)

- Follow the repo’s `pyproject.toml` settings.
- Keep imports clean and sorted via ruff; remove unused imports/vars.
- Prefer readable names and early returns over nested branching.
- Don’t introduce “clever” helpers that hide behavior.

## Comments

- Do not add trivial comments.
- Add comments only when intent is not obvious from the code (business rules, constraints, non-obvious edge cases, workarounds).

## Django guidance

### Models

- Prefer constraints (`UniqueConstraint`, `CheckConstraint`) for invariants.
- Keep model methods small; use a service module for multi-model workflows.
- Prefer `TextChoices`/`IntegerChoices` for enums.

### Views / Templates

- Keep template context minimal and explicit.
- Avoid complex logic in templates; do computation in Python and pass results in context.
- Use Django’s built-in security defaults (autoescaping, CSRF protection).
- Use Django's own i18n and message system for all user facing strings.

### Forms

- Use Django forms for server-rendered flows and validation.
- Put input validation in forms; put cross-entity domain rules in services.

### Queries

- Avoid N+1: use `select_related` / `prefetch_related` where needed.
- Keep query logic close to usage unless shared across multiple call sites.
- Prefer simple QuerySets over custom managers unless they add clear value.

### Transactions

- Use `transaction.atomic()` for multi-step writes that must be consistent.
- Keep atomic blocks tight.

### Settings

- Keep configuration in settings modules and environment variables.
- Don’t hardcode secrets; never commit secrets.

## django-ninja guidance

- Treat Ninja endpoints as API boundaries: validate input with schemas, return typed outputs.
- Keep API handlers thin; call services for business logic.
- Prefer explicit status codes and error shapes; don’t leak internal exceptions.
- Use Django auth/permissions consistently; avoid custom ad-hoc checks in handlers.

## Frontend (templates + native JS)

- No SPA framework; keep JS small and scoped per page.
- Prefer progressive enhancement:
  - pages work without JS when feasible
  - JS enhances interactivity (fetch, inline updates)
- Use `fetch()` to call django-ninja APIs where appropriate.
- Keep DOM manipulation simple; avoid building mini-frameworks.
- Keep static assets organized:
  - `static/<app>/...` and `templates/<app>/...` (or match existing layout)
- Use CSRF correctly for unsafe methods:
  - include `{% csrf_token %}` in forms
  - for `fetch()` POST/PUT/PATCH/DELETE, send the CSRF token header from the cookie.

## Testing

- Add/update tests for behavior changes.
- Prefer testing observable behavior:
  - Django views/templates: status codes, redirects, rendered content, DB state
  - Ninja APIs: response codes, JSON shape, DB state
- Keep tests deterministic; avoid reliance on ordering unless defined.
- For bug fixes, include a regression test.

## Migrations

- Always add migrations for model changes.
- Keep migrations small and reversible when possible.
- Don’t edit applied migrations; create a new one.

## Security

- Never log secrets or sensitive personal data.
- Validate user input on the server.
- Use Django’s built-in protections (CSRF, escaping) as intended.

## Deliverable checklist

- Ruff passes (per `pyproject.toml`).
- Tests updated and passing.
- No unused imports/dead code.
- No unnecessary abstraction; straightforward implementation.
- Comments only where intent is non-obvious.
