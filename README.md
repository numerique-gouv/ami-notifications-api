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

### Linter and formatter: ruff

[ruff](https://docs.astral.sh/ruff/) is "An extremely fast Python linter and
code formatter, written in Rust."

Ruff is used both for linting and formatting:
```shell
make lint-and-format
```

### Linter: biome

[Biome](https://biomejs.dev/) is "One toolchain for your web project"

Biome is used for:
- formatting: `npx @biomejs/biome format --write`

### API

[litestar](https://docs.litestar.dev/latest/index.html) "is a powerful,
flexible, highly performant, and opinionated ASGI framework."

First, you need a local `.env` file:
```sh
cp .env.template .env
```

Then start the server using:
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

### Webpush

Web push is the technology/protocol used to send notifications to a web browser,
and to the tab or pwa associated.

We use the [webpush python library](https://pypi.org/project/webpush/) to deal with the
[VAPID encryption](https://blog.mozilla.org/services/2016/08/23/sending-vapid-identified-webpush-notifications-via-mozillas-push-service/)
for us.

This needs three keys to be generated and loaded when the server start:
- `public_key.pem`
- `private_key.pem`
- `applicationServerKey`

If those aren't present on the disk at the root of this project, and are not set using
env variables (to be used during the scalingo deployment), then running `make dev`
or any variant that calls the `bin/start.sh` file will automatically generate them.

To generate them manually:
```sh
uv run vapid-gen
```

**WARNING**: generating keys will overwrite the existing ones that were used
when storing the user registrations in the database. Changing the keys means the
existing registrations are now obsolete, and can't be used anymore.

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

#### Migrations

We use [alembic](https://alembic.sqlalchemy.org) for database migrations
(changing from one database schema to another).

The base command to run the migrations and update to the latest database schema is:
```sh
uv run --env-file .env alembic upgrade head
```

or simpler:
```sh
make migrate
```

##### Changing the database schema

When changing the models, create a new migration to reflect those changes in
the database:
```sh
uv run --env-file .env alembic revision --autogenerate -m "Explicit message here"
```

This should generate a migration file in `migrations/versions/<some
id>_explicit_message_here.py...`, which you'll then modify according to your
needs.

It should already have some code automatically generated to accomodate the
changes.

##### Rolling back a schema change

To list the existing migrations:
```sh
uv run --env-file .env alembic history
```

Then, to rollback (downgrade) to a previous revision (version):
```sh
uv run --env-file .env alembic downgrade <revision>
```

### Tests

The easiest way to run tests is to use the Makefile target:
```
make test
```

If you'd rather run the tests manually, copy and paste the command from the Makefile:
```
uv run --env-file .env.tests pytest
```


To run a single test, you would use something like:
```
uv run --env-file .env.tests pytest tests/test_basic.py::test_homepage_title
```

### Mobile app

The current mobile app is a
[PWA](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps), built
using [Svelte](https://svelte.dev/).

To build it, either:
```
cd public/mobile-app
npm ci
npm run build
```

Or simpler:
```
make build-app
```

### Contributing

Please check the [CONTRIBUTING.md](CONTRIBUTING.md) file.
