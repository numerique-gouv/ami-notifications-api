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
