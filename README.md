# AMI notifications API

This is the AMI (Application Mobile Interministérielle) notifications API,
providing entry points to create and list notifications, and to store push URLs
registered from clients (web or mobile).


## Tech stack

### Language: python

[python](https://docs.python.org) using
[mypy](https://mypy.readthedocs.io/en/latest/).

### Package and project manager: uv

[uv](https://docs.astral.sh/uv/) is "An extremely fast Python package and
project manager, written in Rust.", and is used to setup and manage the project.

Please follow the [installation
instructions](https://docs.astral.sh/uv/getting-started/installation/) to set it
up on your machine.

Once it's installed, it should be used for everything project related:
- adding more dependencies: `uv add (--dev) <dependency, eg: requests>`
- running a script (or editor) in the project's python environment: `uv run
<command, eg: code>`

### Linter: ruff

[ruff](https://docs.astral.sh/ruff/) is "An extremely fast Python linter and
code formatter, written in Rust."

Ruff is used both for:
- linting: `uv run ruff check --fix`
- formatting: `uv run ruff format`

### API

[litestar](https://docs.litestar.dev/latest/index.html) "is a powerful,
flexible, highly performant, and opinionated ASGI framework."

Start it using:
```sh
uv run litestar run
```

or simply:
```sh
make dev # With live reloading
```

Then access http://127.0.0.1:8000, or open one of:
- http://127.0.0.1:8000/schema (for ReDoc)
- http://127.0.0.1:8000/schema/swagger (for Swagger UI)
- http://127.0.0.1:8000/schema/elements (for Stoplight Elements)
- http://127.0.0.1:8000/schema/rapidoc (for RapiDoc)

### Database: postgresql

[postgresql](https://www.postgresql.org/) with
[asyncpg](https://magicstack.github.io/asyncpg/current/).

If developping locally, and no `DATABASE_URL` env variable is set, it'll default
back to using sqlite.

The `DATABASE_URL` should look like the following:
```
postgresql+asyncpg://[user]:[password]@[url]:[port]/[dbname]
```

For example for a `postgres` database running locally:
```
postgresql+asyncpg://postgres:some_password@localhost:5432/postgres
```
