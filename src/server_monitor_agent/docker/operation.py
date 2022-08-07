
import json

from server_monitor_agent.agent import operation as agent_operation
from server_monitor_agent.docker import model


def container_ls(name: str) -> model.DockerContainerResult:
    if not name or not name.strip():
        raise ValueError("Must provide docker container name or id.")

    args = [
        "docker",
        "inspect",
        "--format",
        '{"ID":"{{ .Id }}", "Inspect": {{json .State }}, "Name":"{{ .Name }}"}',
        name,
    ]
    result = agent_operation.execute_process(args)
    if result.returncode != 0:
        return model.DockerContainerResult(name=name, exit_code=result.returncode)

    data = json.loads(result.stdout)
    inspect = data.get("Inspect")
    state = inspect.get("Status")
    health = inspect.get("Health", {}).get("Status", None)
    return model.DockerContainerResult(
        exit_code=result.returncode,
        name=data.get("Name").strip("/"),
        id=data.get("ID"),
        state=state,
        health=health,
    )
