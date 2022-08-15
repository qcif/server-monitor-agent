import beartype

from server_monitor_agent.agent import model as agent_model
from server_monitor_agent.service.consul import (
    model as consul_model,
    operation as consul_op,
)


@beartype.beartype
def health_checks_input(
    args: consul_model.HealthCheckCollectArgs,
) -> agent_model.AgentItem:
    return consul_op.health_checks(args.to_settings, args.state).to_agent_item()


register_io = [
    agent_model.RegisterCollectInput(health_checks_input),
]
