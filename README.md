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
- formatting: `npx @biomejs/biome check --write`

### API

[Django](https://docs.djangoproject.com/) "was invented to meet fast-moving newsroom deadlines, while satisfying the tough requirements of experienced web developers."

Start the server using:
```sh
make dev # With live reloading
```

It will start a server on https://localhost:8000, it is accessible but actual
accesses will go through the Svelte/Mobile app local server. (see below)

For any specific env variables, create (or edit) a `.env.local` file. Anything in here
will overload what's in the `.env` file.

### Database: postgresql

[postgresql](https://www.postgresql.org/) with
[asyncpg](https://magicstack.github.io/asyncpg/current/).

The `DATABASE_URL` should look like the following:
```
postgresql://[user]:[password]@[url]:[port]/[dbname]
```

For example for a `postgres` database running locally:
```
postgresql://postgres:some_password@localhost:5432/postgres
```

#### Setting up PostgreSQL with Docker

The easiest way to run PostgreSQL locally for development is using Docker,
please check the relevant entry in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

#### Migrations

We use [django migrations](https://docs.djangoproject.com/en/6.0/topics/migrations/) for database migrations
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

For development running ```npm ci --include "dev" && npm run dev``` (or just
```npm run dev``` if there were no changes to dependencies) from the
```public/mobile-app/``` directory.


### User connection

We're using FranceConnect to identify and authorize users, check the
[CONTRIBUTING.md](CONTRIBUTING.md) file for more information on how to use it
locally during development.

### Contributing

Please check the [CONTRIBUTING.md](CONTRIBUTING.md) file.
