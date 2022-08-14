# Development

This document outlines the development process.


## Set up the local development environment


This is only necessary if you will be changing the Python source code.

Install the version of Python specified in the pyproject.toml file.

Create a Python 3 venv in a directory named `venv` in the same level as the cloned directory.

Use pip to install and update the dependencies:

```bash
python -m venv ../venv

# For Windows Git Bash
source ../.venv/Scripts/activate
# others
source ../.venv/bin/activate

python -m pip install -U pip setuptools wheel
pip install -U -r requirements.txt -r requirements-dev.txt
pip list --outdated
```


To run tests and linters (run these before committing), see the github 

```bash
python -X dev -m pytest --tb=line
python -X dev -m coverage run -m pytest --tb=line
python -X dev -m coverage report
python -X dev -m coverage html
python -X dev -m flake8 src --count --show-source --statistics
python -X dev -m black --check .
python -X dev -m mypy src
python -X dev -m pylint src
python -X dev -m pydocstyle src
python -X dev -m pyright src
```

## Build and publish a new release

TODO:
- process?
- automated via github actions, circleci?
- Installed via a pip wheel or self-contained binary?


## Generate OpenAPI client from Prometheus Alertmanager

- Specification: https://raw.githubusercontent.com/prometheus/alertmanager/main/api/v2/openapi.yaml
- OpenAPI generator: https://github.com/openapi-generators/openapi-python-client
- Convert to OpenAPI 3: https://mermade.org.uk/openapi-converter
- Save to: api/prometheus-alertmanager-openapi-3.yml


```bash

cd server-monitor-agent/api

# For Windows Git Bash
source ../.venv/Scripts/activate
# others
source ../.venv/bin/activate

openapi-python-client.exe generate \
  --path prometheus-alertmanager-openapi-3.yml \
  --meta poetry
openapi-python-client.exe update \
  --path prometheus-alertmanager-openapi-3.yml \
  --meta poetry
```
