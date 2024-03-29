import logging
import pathlib
import subprocess
import sys

import beartype
import click
import yaml
from beartype import typing

import importlib_resources
import importlib_metadata

from server_monitor_agent.agent import model as agent_model

logger = logging.getLogger(agent_model.APP_NAME_UNDER)


@beartype.beartype
def execute_process(args: typing.Sequence[str]):
    """Execute a process using the given args."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            shell=False,
            timeout=10,
            check=False,
            text=True,
        )
        print(f"Process result: {result}", file=sys.stderr)
        return result
    except FileNotFoundError as e:
        raise ValueError(f"Error running '{' '.join(args)}'") from e


@beartype.beartype
def log_msg(level: int, msg: str) -> None:
    if logger.isEnabledFor(level):
        if level == logging.INFO:
            click.echo(msg)
        elif level in [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.DEBUG]:
            click.echo(msg, err=True)
        else:
            logger.log(level, msg)


@beartype.beartype
def report_code_from_level(level: str):
    """Convert a report code to report level."""
    if level == agent_model.REPORT_LEVEL_PASS:
        return agent_model.REPORT_CODE_PASS
    elif level == agent_model.REPORT_LEVEL_WARN:
        return agent_model.REPORT_CODE_WARN
    elif level == agent_model.REPORT_LEVEL_CRIT:
        return agent_model.REPORT_CODE_CRIT
    else:
        raise ValueError(f"Unknown report level '{level}'.")


@beartype.beartype
def report_level_from_code(code: str):
    """Convert a report level to report code."""
    if code == agent_model.REPORT_LEVEL_PASS:
        return agent_model.REPORT_LEVEL_PASS

    if code == agent_model.REPORT_CODE_WARN:
        return agent_model.REPORT_LEVEL_WARN

    if code == agent_model.REPORT_CODE_CRIT:
        return agent_model.REPORT_LEVEL_CRIT

    raise ValueError(f"Unknown report code '{code}'.")


@beartype.beartype
def report_evaluate(value: float, test: float) -> typing.Tuple[str, str]:
    """Evaluate a value and test to report whether the value is less than the test."""
    if value < test:
        status_code = agent_model.REPORT_CODE_PASS
        status = agent_model.REPORT_LEVEL_PASS
    elif value == test:
        status_code = agent_model.REPORT_CODE_WARN
        status = agent_model.REPORT_LEVEL_WARN
    else:
        status_code = agent_model.REPORT_CODE_CRIT
        status = agent_model.REPORT_LEVEL_CRIT

    return status, status_code


@beartype.beartype
def get_version() -> typing.Optional[str]:
    """Get the version of this package."""
    try:
        dist = importlib_metadata.distribution(agent_model.APP_NAME_DASH)
        return dist.version
    except importlib_metadata.PackageNotFoundError:
        # ignore error
        pass

    try:
        with importlib_resources.path(agent_model.APP_NAME_UNDER, "entry.py") as p:
            return (p.parent.parent.parent / "VERSION").read_text().strip()
    except FileNotFoundError:
        # ignore error
        pass

    return "(version not available)"


@beartype.beartype
def read_config(path: pathlib.Path) -> typing.Optional[typing.Dict[str, typing.Any]]:
    with path.open("rt") as f:
        return yaml.safe_load(f)


@beartype.beartype
def make_options(name: str, item: typing.Any, available: typing.Iterable[str]) -> str:
    opts = ",".join(available or ["(none)"])
    return f"Unrecognised {name}: '{item}'. Must be one of '{opts}'."


@beartype.beartype
def raise_options(name: str, item: typing.Any, available: typing.Iterable[str]) -> None:
    raise ValueError(make_options(name, item, available))
