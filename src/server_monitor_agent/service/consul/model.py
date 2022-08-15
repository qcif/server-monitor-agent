import dataclasses
import functools
import pathlib

import beartype
import requests
from beartype import typing

from server_monitor_agent.agent import model as agent_model


@beartype.beartype
@dataclasses.dataclass
class ConsulWatchExternalItem(agent_model.ExternalItem):
    """A consul watch item that can be a collect source."""

    # https://www.consul.io/docs/dynamic-app-config/watches

    node: str  # consul: node name
    check_id: str  # consul: unique check id
    name: str  # consul: displayed name
    status: str  # consul: check status:
    # Exit code 0 - Check is 'passing',
    # Exit code 1 - Check is 'warning',
    # Any other code - Check is 'critical'
    notes: str  # consul: opaque to consul - human-readable - from watch definition
    output: str  # consul: output from command
    service_id: str  # consul: unique service id
    service_name: str  # consul: non-unique service name

    @classmethod
    @beartype.beartype
    def from_item(cls, item: dict) -> "ConsulWatchExternalItem":
        return ConsulWatchExternalItem(
            node=item["Node"],
            check_id=item["CheckID"],
            name=item["Name"],
            status=item["Status"],
            notes=item["Notes"],
            output=item["Output"],
            service_id=item["ServiceID"],
            service_name=item["ServiceName"],
        )

    @classmethod
    @beartype.beartype
    def from_items(
        cls, items: typing.List[dict]
    ) -> typing.List["ConsulWatchExternalItem"]:
        return [cls.from_item(item) for item in items]


@beartype.beartype
@dataclasses.dataclass
class ConsulHealthCheckExternalItem(agent_model.ExternalItem):
    """A consul health check status item."""

    # https://www.consul.io/api-docs/health#list-checks-in-state

    node: str  # consul: node name
    check_id: str  # consul: unique check id
    name: str  # consul: displayed name
    status: str  # consul: check status:
    # Exit code 0 - Check is 'passing',
    # Exit code 1 - Check is 'warning',
    # Any other code - Check is 'critical'
    notes: str  # consul: opaque to consul - human-readable - from watch definition
    output: str  # consul: output from command
    service_id: str  # consul: unique service id
    service_name: str  # consul: non-unique service name
    service_tags: list[str]  # consul: tags applied to the service
    namespace: str  # consul: enterprise-only namespace

    @classmethod
    @beartype.beartype
    def from_item(cls, item: dict) -> "ConsulHealthCheckExternalItem":
        return ConsulHealthCheckExternalItem(
            node=item["Node"],
            check_id=item["CheckID"],
            name=item["Name"],
            status=item["Status"],
            notes=item["Notes"],
            output=item["Output"],
            service_id=item["ServiceID"],
            service_name=item["ServiceName"],
            service_tags=item["ServiceTags"],
            namespace=item["Namespace"],
        )

    @classmethod
    @beartype.beartype
    def from_items(
        cls, items: typing.List[dict]
    ) -> typing.List["ConsulHealthCheckExternalItem"]:
        return [cls.from_item(item) for item in items]


@beartype.beartype
@dataclasses.dataclass
class HealthCheckCollectArgs(agent_model.CollectArgs):
    http_addr: typing.Optional[str] = None
    http_ssl_enabled: typing.Optional[bool] = None
    http_ssl_verify: typing.Optional[bool] = None
    ca_cert_file: typing.Optional[pathlib.Path] = None
    ca_cert_dir: typing.Optional[pathlib.Path] = None
    client_cert: typing.Optional[pathlib.Path] = None
    client_key: typing.Optional[pathlib.Path] = None

    @functools.cached_property
    @beartype.beartype
    def to_settings(self) -> "ConsulConnectionSettings":
        return ConsulConnectionSettings(
            http_addr=self.http_addr,
            http_ssl_enabled=self.http_ssl_enabled or False,
            http_ssl_verify=self.http_ssl_verify or False,
            ca_cert_file=self.ca_cert_file,
            ca_cert_dir=self.ca_cert_dir,
            client_cert=self.client_cert,
            client_key=self.client_key,
        )


@beartype.beartype
@dataclasses.dataclass
class ConsulConnectionSettings:
    http_addr: str
    http_ssl_enabled: bool
    http_ssl_verify: bool
    ca_cert_file: typing.Optional[pathlib.Path] = None
    ca_cert_dir: typing.Optional[pathlib.Path] = None
    client_cert: typing.Optional[pathlib.Path] = None
    client_key: typing.Optional[pathlib.Path] = None

    @beartype.beartype
    def request_api(self, path: str) -> requests.Response:
        if not self.http_addr:
            raise ValueError("Consul settings are invalid: must provide http_addr.")

        base_url = f"{self.http_addr}/v1"

        if self.http_ssl_enabled and not self.http_addr.startswith("https"):
            raise ValueError(
                "Consul settings are inconsistent: ssl is enabled but http_addr does not start with 'https'."
            )

        if self.ca_cert_file and self.http_ssl_enabled:
            verify = str(self.ca_cert_file)
        else:
            verify = self.http_ssl_verify

        if self.client_cert and not self.client_cert.exists():
            raise ValueError(
                f"Consul client cert file is specified but does not exist: {self.client_cert}."
            )

        if self.client_key and not self.client_key.exists():
            raise ValueError(
                f"Consul client key file is specified but does not exist: {self.client_key}."
            )

        if self.client_cert and self.client_key:
            cert = (str(self.client_cert), str(self.client_key))
        else:
            cert = None

        req = requests.get(f"{base_url}/{path}", verify=verify, cert=cert)

        if req.status_code != 200:
            raise ValueError(f"Consul http api error {req.status_code}: {req.text}")

        return req
