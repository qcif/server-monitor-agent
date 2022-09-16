import json

import yaml

from server_monitor_agent.agent import model as agent_model, operation as agent_op


def from_agent_item(
    item: agent_model.AgentItem, data_type: str
) -> agent_model.ExternalItem:
    from server_monitor_agent.service.alert_manager import model as alert_model
    from server_monitor_agent.service.consul import model as consul_model

    options = {
        agent_model.AgentItem.data_type_name(): agent_model.AgentItem.from_agent_item,
        alert_model.AlertManagerItem.data_type_name(): alert_model.AlertManagerItem.from_agent_item,
        consul_model.ConsulWatchCheckItem.data_type_name(): consul_model.ConsulWatchCheckItem.from_agent_item,
        consul_model.ConsulHealthCheckStateItem.data_type_name(): consul_model.ConsulHealthCheckStateItem.from_agent_item,
    }

    for name, func in options.items():
        if data_type == name:
            return func(item)

    agent_op.raise_options("data type", data_type, options.keys())


def to_agent_item(
    item: agent_model.ExternalItem, data_type: str
) -> agent_model.AgentItem:
    from server_monitor_agent.service.alert_manager import model as alert_model
    from server_monitor_agent.service.consul import model as consul_model

    options = {
        agent_model.AgentItem.data_type_name(),
        alert_model.AlertManagerItem.data_type_name(),
        consul_model.ConsulWatchCheckItem.data_type_name(),
        consul_model.ConsulHealthCheckStateItem.data_type_name(),
    }

    for name in options:
        if data_type == name:
            return item.to_agent_item()

    agent_op.raise_options("data type", data_type, options)


def from_content(content: str, serialise_format: str) -> agent_model.ExternalItem:
    if not serialise_format:
        raise ValueError("Must provide serialise format.")

    options = {
        "json": json.loads,
        "yaml": yaml.safe_load,
    }

    for fmt, func in options.items():
        if fmt == serialise_format:
            return func(content)

    agent_op.raise_options("serialise format", serialise_format, options.keys())


def to_content(item: agent_model.ExternalItem, serialise_format: str) -> str:
    options = {
        "json": json.dumps,
        "yaml": yaml.safe_dump,
    }

    for fmt, func in options.items():
        if fmt == serialise_format:
            return func(item.to_dict())

    agent_op.raise_options("serialise format", serialise_format, options.keys())
