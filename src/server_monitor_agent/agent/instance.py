import pathlib

import psutil

from server_monitor_agent.agent import common


def memory_usage_detail(time_zone: str, threshold: int) -> common.CheckReport:
    """Get the memory information."""
    result = psutil.virtual_memory().percent

    if result > threshold:
        return common.report_problem(
            time_zone=time_zone,
            check_type="memory",
            check_name="memory",
            description=f"Memory usage is too high ({result}% is over {threshold}%).",
            impact="The server may become slow or unresponsive.",
            action="Check for processes using excessive memory and "
            "determine why the processes are behaving unexpectedly.",
        )
    else:
        return common.report_ok(
            time_zone=time_zone,
            check_type="memory",
            check_name="memory",
            description=f"Memory usage was too high (over {threshold}%, now {result}%).",
            resolution="Memory usage has reduced below the threshold.",
        )


def cpu_usage_detail(
    time_zone: str, threshold: int, interval: float
) -> common.CheckReport:
    """Get the cpu usage."""
    result = psutil.cpu_percent(interval=interval)

    if result > threshold:
        return common.report_problem(
            time_zone=time_zone,
            check_type="cpu",
            check_name="cpu",
            description="Total CPU usage is too high "
            f"({result}% is over {threshold}%).",
            impact="The server may become slow or unresponsive.",
            action="Check for processes using excessive CPU and "
            "determine why the processes are behaving unexpectedly.",
        )
    else:
        return common.report_ok(
            time_zone=time_zone,
            check_type="cpu",
            check_name="cpu",
            description="Total CPU usage was too high "
            f"(over {threshold}%, now {result}%).",
            resolution="Total CPU usage has reduced below the threshold.",
        )


def disk_usage(mount_path: pathlib.Path) -> float:
    """Get the usage of the disk mounted at the given path."""
    keys = ["source", "fstype", "size", "used", "avail", "pcent", "file", "target"]
    args = [
        "df",
        "--exclude-type=devtmpfs",
        "--exclude-type=tmpfs",
        "--exclude-type=squashfs",
        f"--output={','.join(keys)}",
    ]
    result = common.execute_process(args)
    lines = result.stdout.splitlines()[1:]
    data = [dict(zip(keys, i.split())) for i in lines]
    match_data = [i for i in data if i["target"] == str(mount_path)]

    if len(match_data) != 1:
        matched_targets = ", ".join(sorted([i["target"] for i in match_data]))
        available_targets = ", ".join(sorted([i["target"] for i in data]))
        raise ValueError(
            f"Cannot match mount point '{str(mount_path)}' to one mount. \n"
            f"It matched {len(match_data)}: '{matched_targets}'. \n"
            f"Available mounts: '{available_targets}'."
        )
    disk_size = int(match_data[0]["size"])
    disk_used = int(match_data[0]["used"])
    percent = round((disk_used / disk_size) * 100.0, 2)
    return percent


def disk_usage_detail(
    time_zone: str, threshold: int, mount_path: pathlib.Path
) -> common.CheckReport:
    result = disk_usage(mount_path=mount_path)

    if result > threshold:
        return common.report_problem(
            time_zone=time_zone,
            check_type="disk",
            check_name="disk",
            description=f"Disk used space for '{mount_path}' is too high "
            f"({result}% is over {threshold}%).",
            impact="There may not be enough space for normal operation. "
            "The disk may fill and cause the server serious issues.",
            action="Check for unexpected files, such as logs or exception records, "
            "and archive some files to create space.",
        )
    else:
        return common.report_ok(
            time_zone=time_zone,
            check_type="disk",
            check_name="disk",
            description=f"Disk used space for '{mount_path}' was too high "
            f"(over {threshold}%, now {result}%).",
            resolution="There is now enough disk free space.",
        )
