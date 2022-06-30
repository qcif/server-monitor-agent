# Development

This document outlines the development process.


## Set up the local development environment

TODO:
- Uses pipenv and Pipfile to manage Python packages?


This is only necessary if you will be changing the Python source code.

Install the version of Python specified in the pyproject.toml file.

Create a Python 3 venv in a directory named `venv` in the same level as the cloned directory.

Use pip and pipenv to install and update the dependencies:

    $ python -m venv ../venv
    $ ../venv/bin/activate
    $ python -m pip install -U pip setuptools wheel pipenv
    $ pip list --outdated
    $ pipenv install --dev

To run tests and linters (run these before committing):

    $ pipenv run python -X dev -m pytest --tb=line
    $ pipenv run python -X dev -m coverage run -m pytest
    $ pipenv run python -X dev -m coverage report
    $ pipenv run python -X dev -m coverage html
    $ pipenv run python -X dev -m flake8 . --count --show-source --statistics
    $ pipenv run python -X dev -m black --check .
    $ pipenv run python -X dev -m mypy src
    $ pipenv run python -X dev -m pylama

## Build and publish a new release

TODO:
- process?
- automated via github actions, circleci?
- Installed via a pip wheel or self-contained binary?
