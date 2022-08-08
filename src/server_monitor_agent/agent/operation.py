import pathlib
import subprocess
import sys
import typing

import yaml

try:
    from importlib import metadata
except ImportError:
    import importlib_metadata as metadata

try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources

from server_monitor_agent.agent import model as agent_model


def execute_process(args: typing.Sequence[str]):
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            shell=False,
            timeout=10,
            check=False,
            text=True,
        )
        return result
    except FileNotFoundError as e:
        raise ValueError(f"Error running '{' '.join(args)}'") from e


def report_choices() -> typing.List[str]:
    return [
        agent_model.REPORT_LEVEL_PASS,
        agent_model.REPORT_LEVEL_WARN,
        agent_model.REPORT_LEVEL_CRIT,
    ]


def report_code_from_level(level: str):
    if level == agent_model.REPORT_LEVEL_PASS:
        return agent_model.REPORT_CODE_PASS
    elif level == agent_model.REPORT_LEVEL_WARN:
        return agent_model.REPORT_CODE_WARN
    elif level == agent_model.REPORT_LEVEL_CRIT:
        return agent_model.REPORT_CODE_CRIT
    else:
        raise ValueError(f"Unknown report level '{level}'.")


def report_level_from_code(code: str):
    if code == agent_model.REPORT_LEVEL_PASS:
        return agent_model.REPORT_LEVEL_PASS

    if code == agent_model.REPORT_CODE_WARN:
        return agent_model.REPORT_LEVEL_WARN

    if code == agent_model.REPORT_CODE_CRIT:
        return agent_model.REPORT_LEVEL_CRIT

    raise ValueError(f"Unknown report code '{code}'.")


def report_evaluate(value: float, test: float) -> typing.Tuple[str, str]:
    if value > test:
        status_code = agent_model.REPORT_CODE_CRIT
        status = agent_model.REPORT_LEVEL_CRIT
    elif value == test:
        status_code = agent_model.REPORT_CODE_WARN
        status = agent_model.REPORT_LEVEL_WARN
    else:
        status_code = agent_model.REPORT_CODE_PASS
        status = agent_model.REPORT_LEVEL_PASS

    return status, status_code


def get_version() -> typing.Optional[str]:
    """Get the version of this package."""
    try:
        dist = metadata.distribution(agent_model.APP_NAME_DASH)
        return dist.version
    except metadata.PackageNotFoundError:
        # ignore error
        pass

    try:
        with resources.path(agent_model.APP_NAME_UNDER, "entry.py") as p:
            return (p.parent.parent.parent / "VERSION").read_text().strip()
    except FileNotFoundError:
        # ignore error
        pass

    return None


def read_config(path: pathlib.Path) -> typing.Optional[dict[str, typing.Any]]:
    with path.open("rt") as f:
        return yaml.safe_load(f)


def make_options(items: typing.Iterable[str]) -> str:
    opts = "', '".join(items or ["(none)"])
    return f"'{opts}'"


def write_stream(out_format: str, out_target: str, item: agent_model.AgentItem) -> None:
    # get content
    if out_format == agent_model.FORMAT_AGENT:
        content = item.to_json()
    else:
        options = make_options(agent_model.OUT_FORMATS)
        raise ValueError(
            f"Unrecognised format for output: {out_format}. "
            f"Must be one of {options}."
        )

    # write content
    if out_target == agent_model.STREAM_STDOUT:
        sys.stdout.write(content)

    elif out_target == agent_model.STREAM_STDERR:
        sys.stderr.write(content)

    else:
        options = make_options(agent_model.STREAM_TARGETS)
        raise ValueError(
            f"Unrecognised stream write target '{out_target}'. "
            f"Must be one of {options}."
        )


def write_file(out_format: str, out_target: pathlib.Path, item: agent_model.AgentItem):
    # get content
    if out_format == agent_model.FORMAT_AGENT:
        content = item.to_json()
    else:
        options = make_options(agent_model.OUT_FORMATS)
        raise ValueError(
            f"Unrecognised format for file output: {out_format}. "
            f"Must be one of {options}."
        )

    # write content
    if not out_target:
        raise ValueError(f"Must provide path to write.")

    out_target.parent.mkdir(parents=True, exist_ok=True)
    out_target.write_text(content, encoding="utf8")


def read_stream(in_format: str, in_source: str) -> agent_model.AgentItem:
    # read content
    if in_source == agent_model.STREAM_STDIN:
        content = sys.stdin.read()
    else:
        options = make_options(agent_model.STREAM_SOURCES)
        raise ValueError(
            f"Unrecognised stream read source '{in_source}'. "
            f"Must be one of {options}."
        )
    # get content
    if in_format == agent_model.FORMAT_AGENT:
        return agent_model.AgentItem.from_json(content)

    if in_format == agent_model.FORMAT_CONSUL_WATCH:
        return agent_model.AgentItem.from_consul_watch(content)

    options = make_options(agent_model.IN_FORMATS)
    raise ValueError(
        f"Unrecognised format for stream input: {in_format}. "
        f"Must be one of {options}"
    )


def read_file(
    in_format: str,
    in_target: pathlib.Path,
) -> agent_model.AgentItem:
    # read content
    if not in_target or not in_target.exists():
        raise ValueError(f"File to read must exist: '{in_target}'.")

    content = in_target.read_text(encoding="utf8")

    # get content
    if in_format == agent_model.FORMAT_AGENT:
        return agent_model.AgentItem.from_json(content)

    if in_format == agent_model.FORMAT_CONSUL_WATCH:
        return agent_model.AgentItem.from_consul_watch(content)

    options = make_options(agent_model.IN_FORMATS)
    raise ValueError(
        f"Unrecognised format for file input: {in_format}." f"Must be one of {options}"
    )
