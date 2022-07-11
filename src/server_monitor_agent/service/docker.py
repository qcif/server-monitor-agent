import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from server_monitor_agent.common import ConfigEntryMixin, ProgramMixin, RunArgs
from server_monitor_agent.common import ResultMixin, ReportMixin
from server_monitor_agent.core.local import LocalProgram
from server_monitor_agent.service.agent import AgentItem


@dataclass
class CheckDockerContainerEntry(ConfigEntryMixin, ReportMixin):
    name: str
    state: str
    health: str
    group: str = "check"
    type: str = "docker-container-status"

    def operation(self, run_args: RunArgs) -> None:
        states_running = "running"
        states_not_running = "not-running"
        states_available = [states_running, states_not_running]

        healths_healthy = "healthy"
        healths_ignore = "ignore"
        healths_available = [healths_healthy, healths_ignore]

        if self.state not in states_available:
            raise ValueError(
                f"State must be one of '{', '.join(states_available)}' "
                f"for check '{run_args.name}' ({self.type}'."
            )

        if self.health not in healths_available:
            raise ValueError(
                f"Health must be one of '{', '.join(healths_available)}' "
                f"for check '{run_args.name}' ({self.type}'."
            )

        container_name = self.name

        docker = DockerProgram()
        show = docker.container_ls(container_name)

        if show is None:
            exit_code = 2
            state = ""
            health = None
        else:
            exit_code = show.exit_code
            container_name = show.name
            state = show.state
            health = show.health

        status = self._pass
        status_code = self._pass_code

        descr_items = []
        if self.state == states_running and state != states_running:
            status = self._crit
            status_code = self._crit_code
            descr_items.append("Container was expected to be running, but was not.")

        if self.health == healths_healthy and health is None:
            status = self._warn
            status_code = self._warn_code
            descr_items.append(
                "Container health was expected to be healthy, but was not available."
            )

        if self.health == healths_healthy and health != healths_healthy:
            status = self._crit
            status_code = self._crit_code
            descr_items.append(
                "Container health was expected to be healthy, but it was not."
            )

        if exit_code != 0:
            status = self._crit
            status_code = self._crit_code
            descr_items.append("Container state check was not successful.")

        local = LocalProgram()
        hostname = local.hostname()

        timezone_str = local.timezone()
        timezone = ZoneInfo(timezone_str)
        date = datetime.now(tz=timezone)

        if health is None:
            health = "(no health check)"

        if status == self._pass:
            title = f"Normal container {container_name} state"
            descr = f"Normal container {container_name} state {state} health {health}."
        else:
            title = f"Unexpected container {container_name} state"
            descr = (
                f"Unexpected container {container_name} state {state} health {health}. "
                f"{' '.join(descr_items)}"
            )

        item = AgentItem(
            service_name=f"container {container_name}",
            host_name=hostname,
            source_name="docker",
            status_code=status_code,
            status_name=status,
            title=title,
            description=descr.strip(),
            check_name=self.key,
            check_type=self.type,
            date=date,
            tags={},
        )
        self._do_output(run_args, item)


@dataclass
class DockerContainerResult(ResultMixin):
    name: str

    id: Optional[str] = None
    state: Optional[str] = None
    health: Optional[str] = None


class DockerProgram(ProgramMixin):
    def container_ls(self, name: str) -> Optional[DockerContainerResult]:
        if not name or not name.strip():
            return None

        args = [
            "docker",
            "inspect",
            "--format",
            '{"ID":"{{ .Id }}", "Inspect": {{json .State }}, "Name":"{{ .Name }}"}',
            name,
        ]
        result = self._run_cmd(args)
        if result.returncode != 0:
            return DockerContainerResult(name=name, exit_code=result.returncode)

        data = json.loads(result.stdout)
        inspect = data.get("Inspect")
        state = inspect.get("Status")
        health = inspect.get("Health", {}).get("Status", None)
        return DockerContainerResult(
            exit_code=result.returncode,
            name=data.get("Name").strip("/"),
            id=data.get("ID"),
            state=state,
            health=health,
        )
