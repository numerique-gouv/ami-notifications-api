# CONTRIBUTING

Thanks for wanting to contribute to the project!

If, as a non tech people, you wish to contribute to the behavior scenario, please visit [this page](./CONTRIBUTING-BEHAVIOR.md)!

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

There's a `.env` file that holds all the default env variable values.
For any specific env variables, create (or edit) a `.env.local` file. Anything in here
will overload what's in the `.env` file.

For example you'll need to overload the FranceConnect secrets for AMI and RVO in
your `.env.local` file.

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
uv run --env-file .env --env-file .env.local alembic upgrade head
```

or simpler:
```sh
make migrate
```

##### Changing the database schema

When changing the models, create a new migration to reflect those changes in
the database:
```sh
uv run --env-file .env --env-file .env.local alembic revision --autogenerate -m "Explicit message here"
```

This should generate a migration file in `migrations/versions/<some
id>_explicit_message_here.py...`, which you'll then modify according to your
needs.

It should already have some code automatically generated to accomodate the
changes.

##### Rolling back a schema change

To list the existing migrations:
```sh
uv run --env-file .env --env-file .env.local alembic history
```

Then, to rollback (downgrade) to a previous revision (version):
```sh
uv run --env-file .env --env-file .env.local alembic downgrade <revision>
```

###### Shortcuts

It is possible to upgrade/downgrade schema without targetting a revision.

To update:
```sh
uv run --env-file .env --env-file .env.local alembic upgrade +<n>
```

To downgrade:
```sh
uv run --env-file .env --env-file .env.local alembic downgrade -<n>
```

Example::
```sh
uv run --env-file .env --env-file .env.local alembic upgrade +1
uv run --env-file .env --env-file .env.local alembic downgrade -1
```

##### Reset (empty) the database (useful for demos)

You'll need the
[scalingo's command line interface](https://doc.scalingo.com/tools/cli/start),
then [add your ssh key to your account](https://doc.scalingo.com/tools/cli/introduction),
and then login with:

```sh
scalingo login
```

Once that done, you'll be able to connect to an app's PostgreSQL container:

```sh
scalingo -a ami-back-staging pgsql-console
```

Replace the `ami-back-staging` with the app you want to reset the data, eg
`ami-back-staging-pr179` for the review app for PR #179.

You'll then be able to run the following SQL command:

```sql
truncate ami_user, notification, registration;
```

This will empty those three tables.

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
uv run --env-file .env --env-file .env.local pytest
```

To run a single test, you would use something like:
```
uv run --env-file .env --env-file .env.local pytest tests/test_basic.py::test_homepage_title
```

## France Connect

We're using [France Connect](https://docs.partenaires.franceconnect.gouv.fr/)
to identify and authorize users. During development and on the CI, we have a
sandbox available, with the URLs and Client ID specified in the `.env` file,
and the secrets need to be specified in the `.env.local`.

The Client Secret however, is... well, secret, and is available on the sandbox
[partner's page](https://espace.partenaires.franceconnect.gouv.fr).

You'll need to request access to this partner's page and/or ask us for the
Client Secret before being able to France Connect locally while developping.

At the moment, France Connect is only used in a "test Service provider"
scenario:

### The test Service Provider scenario

- the France Connect button is displayed in the mobile app/PWA
- clicking on it will start the France connection, by redirecting to the France
Connect service
- check the [FC demo users](https://github.com/france-connect/sources/blob/main/docker/volumes/fcp-low/mocks/idp/databases/citizen/base.csv)
for some demo credentials
- at the end of the connection, if successful, the user will be redirected to
the test service provider (on the backend) with the FC auth code, which it'll
use to get the user auth token, which in turn will allow retrieving the user
information from FC, which will finally be stored on the session in the backend,
making it available to query from the mobile app using the `/api/v1/userinfo`
endpoint.

### Creating a PR with access to the FC service

We previously needed a bunch of manual, error-prone steps to configure a review
app to have access to FranceConnect services, as it checks that the
[redirect URLs are properly setup] (https://docs.partenaires.franceconnect.gouv.fr/fs/devenir-fs/projet-bac-a-sable/#configuration-de-votre-instance-de-test),
and we thus had to update the URLs in the
[partner's page](https://espace.partenaires.franceconnect.gouv.fr),
and update the `PUBLIC_SECTOR_IDENTIFIER_URL` env variable in the staging app
on Scalingo.

We now use a
[proxy](https://ami-fc-proxy-dev.osc-fr1.scalingo.io/)
through the configuration of the `FC_PROXY` env variable in the `.env` file, so
none of that is needed anymore, it's all been configured once and for all.
