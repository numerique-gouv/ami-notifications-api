# AMI notifications API

This is the AMI (Application Mobile Interministérielle) notifications API,
providing entry points to create and list notifications, and to store push URLs
registered from clients (web or mobile) amongst other things.


## Tech stack

### Language: python

[python](https://docs.python.org) using
[pyright](https://github.com/microsoft/pyright).

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

Start the server using:
```sh
make dev # With live reloading
```

Then access http://127.0.0.1:8000, or open one of:
- http://127.0.0.1:8000/schema (for ReDoc)
- http://127.0.0.1:8000/schema/swagger (for Swagger UI)
- http://127.0.0.1:8000/schema/elements (for Stoplight Elements)
- http://127.0.0.1:8000/schema/rapidoc (for RapiDoc)

For any specific env variables, create (or edit) a `.env.local` file. Anything in here
will overload what's in the `.env` file.

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

The `DATABASE_URL` should look like the following:
```
postgresql+asyncpg://[user]:[password]@[url]:[port]/[dbname]
```

For example for a `postgres` database running locally:
```
postgresql+asyncpg://postgres:some_password@localhost:5432/postgres
```

#### Setting up PostgreSQL with Docker

The easiest way to run PostgreSQL locally for development is using Docker,
please check the relevant entry in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

#### Migrations

We use [alembic](https://alembic.sqlalchemy.org) for database migrations
(changing from one database schema to another).
You'll find detailed commands and usage in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

### Tests

The easiest way to run tests is to use the Makefile target:
```
make test
```

You'll find detailed commands and usage in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

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

### User connection

We're using France Connect to identify and authorize users, check the
[CONTRIBUTING.md](CONTRIBUTING.md) file for more information on how to use it
locally during development.

### Contributing

Please check the [CONTRIBUTING.md](CONTRIBUTING.md) file.
