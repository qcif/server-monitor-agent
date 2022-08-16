import dataclasses

import beartype

from server_monitor_agent.agent import model as agent_model
from server_monitor_agent.service.consul import (
    model as consul_model,
    operation as consul_op,
)
from server_monitor_agent.service.server import operation as server_op


@beartype.beartype
def health_checks_input(
    args: consul_model.HealthCheckCollectArgs,
) -> agent_model.AgentItem:

    hostname = server_op.hostname()
    date = server_op.timezone().now

    items = consul_op.health_checks(args.to_settings, agent_model.REPORT_LEVEL_ANY)
    checks = [dataclasses.asdict(i) for i in items]

    title = ""
    descr = ""
    status = agent_model.REPORT_LEVEL_PASS
    return agent_model.AgentItem(
        summary=title,
        description=descr.strip(),
        host_name=hostname,
        source_name="consul",
        check_name="health-checks",
        date=date,
        status_name=status,
        service_name=args.name,
        tags={"checks": checks},
    )


register_io = [
    agent_model.RegisterCollectInput(health_checks_input),
]
