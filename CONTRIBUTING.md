# Server monitor agent contributing guide

## Development

Create a virtual environment:

```bash
python -m venv .venv
```

Install runtime dependencies and development dependencies:

```bash
# Windows
.venv\Scripts\activate.ps1

# Linux
source .venv/bin/activate

# install dependencies
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade -r requirements-dev.txt -r requirements.txt

# check for outdated packages
pip list --outdated
```

## Create and upload release

Generate the distribution package archives.

```bash
python -X dev -m build
```

Upload archives to Test PyPI first.

```bash
python -X dev -m twine upload --repository testpypi dist/*
```

When uploading:

- for username, use `__token__`
- for password, create a token at https://test.pypi.org/manage/account/#api-tokens

Go to the [test project page](https://test.pypi.org/project/server-monitor-agent) and check that it looks ok.

Then create a new virtual environment, install the dependencies, and install from Test PyPI.

```bash
python -m venv .venv-test
source .venv-test/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade -r requirements.txt

SERVER_MONITOR_AGENT_VERSION='0.3.0'
pip install --index-url https://test.pypi.org/simple/ --no-deps server-monitor-agent==$SERVER_MONITOR_AGENT_VERSION
```

Test the installed package.

```bash
server-monitor-agent --version
server-monitor-agent --help
server-monitor-agent memory
server-monitor-agent cpu
server-monitor-agent systemd-service --help
server-monitor-agent consul-report aws
```

If the package seems to work as expected, upload it to the live PyPI.

```bash
python -X dev -m twine upload dist/*
```

When uploading:

- for username, use `__token__`
- for password, create a token at https://pypi.org/manage/account/#api-tokens

Go to the [live project page](https://pypi.org/project/server-monitor-agent) and check that it looks ok.

Done!
