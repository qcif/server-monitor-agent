# Development

This document outlines the development process.


## Set up the local development environment


This is only necessary if you will be changing the Python source code.

Install the version of Python specified in the pyproject.toml file.

Create a Python 3 venv in a directory named `venv` in the same level as the cloned directory.

Use pip to install and update the dependencies:

    $ python -m venv ../venv
    $ ../venv/bin/activate
    $ python -m pip install -U pip setuptools wheel
    $ pip list --outdated
    $ pip install -U -r requirements.txt
    $ pip install -U -r requirements-dev.txt

To run tests and linters (run these before committing):

    $ python -X dev -m pytest --tb=line
    $ python -X dev -m coverage run -m pytest --tb=line
    $ python -X dev -m coverage report
    $ python -X dev -m coverage html
    $ python -X dev -m flake8 src --count --show-source --statistics
    $ python -X dev -m black --check .
    $ python -X dev -m mypy src
    $ python -X dev -m pylint src
    $ python -X dev -m pydocstyle src
    $ python -X dev -m pyright src

## Build and publish a new release

TODO:
- process?
- automated via github actions, circleci?
- Installed via a pip wheel or self-contained binary?
