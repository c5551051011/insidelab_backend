# Repository Guidelines

## Project Structure & Module Organization
- Core Django project under `insidelab/`; env configs in `insidelab/settings/` (`development.py`, `production.py`, `test.py`).
- Domain apps live in `apps/` (`authentication`, `universities`, `labs`, `reviews`, `publications`), each with `tests/` and fixtures.
- Utilities: `manage.py`, `scripts/`, `switch_env.sh`, `run_tests.sh`, `templates/`, and sample data in `dataset/`. Root `test_*.py` files cover API and regression cases.

## Build, Test, and Development Commands
- Setup: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`.
- Switch env: `./switch_env.sh dev` or `./switch_env.sh prod` (creates `.env` from templates).
- Database: `python manage.py migrate`; run server with `python manage.py runserver` using the active env.
- Test suite: `./run_tests.sh` (supports selectors like `./run_tests.sh auth`).
- Direct Django tests: `DJANGO_SETTINGS_MODULE=insidelab.settings.test python manage.py test --verbosity=2`.
- Optional pytest: `pytest` or targets such as `pytest apps/authentication/tests/test_models.py::UserModelTest::test_create_user_with_email`.

## Coding Style & Naming Conventions
- PEP 8, 4-space indentation, type hints when useful; concise docstrings for views/serializers.
- Files use `snake_case.py`; classes `CamelCase`; constants `UPPER_SNAKE`; URL/query params `lower_snake`.
- Keep business rules in serializers/managers, not views; prefer DRF validators over manual checks.
- Lint before PRs: `flake8 apps/ insidelab/ --exclude=migrations,__pycache__,venv` and `pylint apps insidelab`.

## Testing Guidelines
- Naming per `pytest.ini`: files `test_*.py`, classes `Test*`, functions `test_*`; markers `unit`, `integration`, `slow`.
- Use fixtures in `conftest.py`; favor factories/helpers over inline object setup.
- Aim for coverage on models, serializers, and API endpoints; add regression tests for every bug fix or new endpoint path.

## Commit & Pull Request Guidelines
- Commits: imperative, concise, ~72 chars (e.g., `Add professor filter to reviews API`); reference issues when present.
- PRs: include summary, scope, env used (`dev`/`prod`), tests run (`./run_tests.sh`, pytest targets, lint), and migration or config notes.
- Provide API examples or screenshots for endpoint/Swagger updates; mention rollback steps for data migrations.
- CI runs flake8, pylint, bandit, safety, and Django tests—match locally to reduce churn.

## Security & Configuration Tips
- Do not commit `.env*` or secrets; rely on `switch_env.sh` and local env files.
- SQLite is fine for quick runs; production uses Postgres—never hard-code credentials in code or tests.
- Redis/cache is optional locally; guard cache-only code paths with configuration checks.
- Strip PII from logs, fixtures, and `dataset/` samples; keep tokens/cookies out of version control.
