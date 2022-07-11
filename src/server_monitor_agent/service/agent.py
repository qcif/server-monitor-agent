import dataclasses
import json
from dataclasses import dataclass
from datetime import datetime
from json import JSONDecodeError


@dataclass
class AgentItem:
    service_name: str
    """The name of the service."""

    host_name: str
    """Name of the server where the event occurred or node name."""

    source_name: str
    """Name of the source of this information, e.g. systemd."""

    status_code: str
    """Code from the service, e.g. 0 for program success or 200 for http ok."""

    status_name: str
    """Status of the check: one of 'passing', 'warning', 'critical'."""

    title: str
    """The headline summary for the check."""

    description: str
    """A free-text description of the service status.
    For a non-passing check, this should include the reason for the failure.
    It might also include hints regarding how to restore the service."""

    check_name: str
    """The name of the check in the config file."""

    check_type: str
    """The type of check in the config file."""

    date: datetime
    """When the information in this item generated or when the event occurred."""

    tags: dict[str, str] = dataclasses.field(default_factory=dict)
    """Optional key=value entries for arbitrary information.
    This may not be displayed in all notifications."""

    def to_json(self) -> str:
        data = dataclasses.asdict(self)

        date_fields = ["date"]
        for date_field in date_fields:
            if data[date_field]:
                data[date_field] = data[date_field].isoformat(timespec="seconds")

        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, value: str) -> "AgentItem":
        try:
            raw = json.loads(value)
        except JSONDecodeError:
            raise ValueError(f"Could not read input in agent format: '{value}'.")

        if not isinstance(raw, dict):
            raise ValueError(f"Could not read input in agent format: '{value}'.")

        item = AgentItem(**raw)
        return item

    @classmethod
    def from_consul_watch(cls, value: str) -> "AgentItem":
        raise NotImplementedError()
