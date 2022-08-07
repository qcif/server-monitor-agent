from server_monitor_agent.consul import model as consul_model


def is_leader() -> bool:
    raise NotImplementedError()


def health_checks(
    args: consul_model.HealthCheckCollectArg,
) -> consul_model.ConsulHealthChecksResult:
    raise NotImplementedError()
