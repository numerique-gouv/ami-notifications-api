# CONTRIBUTING

Thanks for wanting to contribute to the project!

## Initial Setup

The very first thing you'll need to do is to install
[uv](https://docs.astral.sh/uv/), the package manager, and install all the
project dependencies using

```shell
uv sync
```

The next good step is to enable the pre-commit hooks we use to format and lint
the project, for optimum consistency and readability between all the devs:

```shell
uv run pre-commit install
```

This will make sure each and every commit are up to par with our coding habits.

To run it manually:

```shell
uv run pre-commit run --all-files
```

Or simply use the `Makefile` target:

```shell
make lint-and-format
```

The commands executed by the `pre-commit` call are all configured in the
[.pre-commit-config.yaml](.pre-commit-config.yaml) file.

## Database Setup

This project uses PostgreSQL for both development and testing. Follow these steps to set up the database locally using Docker:

### 1. Start PostgreSQL Container

```shell
docker run --name ami-postgres \
  -e POSTGRES_PASSWORD=some_password \
  -e POSTGRES_DB=postgres \
  -p 5432:5432 \
  -d postgres:15
```

### 2. Create Test Database

The test suite requires a separate test database:

```shell
docker exec -it ami-postgres psql -U postgres -c "CREATE DATABASE postgres_test;"
```

### 3. Configure Environment

Copy the environment template and ensure it matches your PostgreSQL setup:

```shell
cp .env.template .env
```

The `.env` file should contain:
```
DATABASE_URL="postgresql+asyncpg://postgres:some_password@localhost:5432/postgres"
```

### 4. Run Database Migrations

Apply the database schema:

```shell
make migrate
```

### 5. Verify Setup

Run the tests to ensure everything is working:

```shell
make test
```

### Managing the Database Container

- **Stop the container:** `docker stop ami-postgres`
- **Start the container:** `docker start ami-postgres`
- **Remove the container:** `docker rm ami-postgres` (you'll need to recreate it and the test database)

### Managing the database schema changes (migrations)

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

## Running tests

Running tests is as easy as:
```sh
make test
```

The tests will be run against a (postgres) database on the same server as the
one configured for your application, with the `_test` suffix.

So for example if you're using
`DATABASE_URL="postgresql+asyncpg://postgres:some_password@localhost:5432/postgres"`
for your application, the tests will be running on
`DATABASE_URL="postgresql+asyncpg://postgres:some_password@localhost:5432/postgres_test"`.

This test database must be created beforehand.

If you'd rather run the tests manually, copy and paste the command from the Makefile:
```
uv run --env-file .env pytest
```

To run a single test, you would use something like:
```
uv run --env-file .env pytest tests/test_basic.py::test_homepage_title
```

