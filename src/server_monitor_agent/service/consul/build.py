import beartype
from beartype import typing

from server_monitor_agent.service.consul import model as consul_model
from server_monitor_agent.service.consul import operation as consul_op


@beartype.beartype
def health_checks(
    args: consul_model.HealthCheckCollectArg,
) -> typing.Iterable[consul_model.ConsulHealthCheckExternalItem]:
    return consul_op.health_checks(args.to_settings, args.state)
