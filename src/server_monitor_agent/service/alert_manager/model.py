import dataclasses
import datetime

import beartype
from beartype import typing

from server_monitor_agent.agent import model as agent_model


@beartype.beartype
@dataclasses.dataclass
class AlertManagerSendArgs(agent_model.SendArgs):
    """"""

    base_url: str


@beartype.beartype
@dataclasses.dataclass
class AlertManagerItem(agent_model.ExternalItem, agent_model.AgentItemConvertMixin):
    labels: typing.Dict
    generator_url: typing.Optional[str] = None
    starts_at: typing.Optional[datetime.datetime] = None
    ends_at: typing.Optional[datetime.datetime] = None
    annotations: typing.Dict = dataclasses.field(default_factory=dict)
    additional_properties: typing.Dict = dataclasses.field(default_factory=dict)

    @classmethod
    def data_type_name(cls):
        return "prom-alert-manager"

    @beartype.beartype
    def to_dict(self) -> typing.Dict:
        data = dataclasses.asdict(self)

        date_fields = ["starts_at", "ends_at"]
        for date_field in date_fields:
            if date_field in data and data[date_field]:
                data[date_field] = data[date_field].isoformat(timespec="seconds")

        return data

    @classmethod
    @beartype.beartype
    def from_dict(cls, item: typing.Dict) -> agent_model.ExternalItem:
        raw = {**item}

        date_fields = ["starts_at", "ends_at"]
        for date_field in date_fields:
            if date_field in raw and raw[date_field]:
                raw[date_field] = datetime.datetime.fromisoformat(raw[date_field])

        return cls(**raw)

    @beartype.beartype
    def to_agent_item(self) -> agent_model.AgentItem:
        key = "alert_manager_item"

        raise NotImplementedError()
        summary = ""
        description = ""
        host_name = ""
        source_name = ""
        check_name = ""
        date = ""
        status_name = ""
        service_name = ""
        extra_data = self.to_dict()
        return agent_model.AgentItem(
            summary=summary,
            description=description,
            host_name=host_name,
            source_name=source_name,
            check_name=check_name,
            date=date,
            status_name=status_name,
            service_name=service_name,
            extra_data={key: extra_data},
        )

    @classmethod
    @beartype.beartype
    def from_agent_item(cls, item: agent_model.AgentItem) -> "AlertManagerItem":
        key = "alert_manager_item"
        if key in item.extra_data:
            return cls(**item.extra_data[key])

        raise NotImplementedError()
        return cls(
            labels={},
            generator_url="",
            starts_at="",
            ends_at="",
            annotations={},
            additional_properties={},
        )
