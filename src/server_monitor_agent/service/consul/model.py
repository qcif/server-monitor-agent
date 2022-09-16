import dataclasses
import functools
import pathlib

import beartype
import requests
from beartype import typing

from server_monitor_agent.agent import model as agent_model


@beartype.beartype
@dataclasses.dataclass
class ConsulWatchCheckItem(agent_model.ExternalItem, agent_model.AgentItemConvertMixin):
    """A consul watch item that can be a collect source."""

    # Docs: https://www.consul.io/docs/dynamic-app-config/watches#checks

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
    def data_type_name(cls):
        return "consul-watch-check"

    @beartype.beartype
    def to_dict(self) -> typing.Dict:
        return {
            "Node": self.node,
            "CheckID": self.check_id,
            "Name": self.name,
            "Status": self.status,
            "Notes": self.notes,
            "Output": self.output,
            "ServiceID": self.service_id,
            "ServiceName": self.service_name,
        }

    @classmethod
    @beartype.beartype
    def from_dict(cls, item: typing.Dict) -> "ConsulWatchCheckItem":
        return ConsulWatchCheckItem(
            node=item["Node"],
            check_id=item["CheckID"],
            name=item["Name"],
            status=item["Status"],
            notes=item["Notes"],
            output=item["Output"],
            service_id=item["ServiceID"],
            service_name=item["ServiceName"],
        )

    @beartype.beartype
    def to_agent_item(self) -> "agent_model.AgentItem":
        key = "consul_watch_check_item"

        raise NotImplementedError()
        summary = ""
        description = ""
        source_name = ""
        check_name = ""
        date = ""
        status_name = ""
        return agent_model.AgentItem(
            summary=summary,
            description=description,
            host_name=self.node,
            source_name=source_name,
            check_name=check_name,
            date=date,
            status_name=status_name,
            service_name=self.service_name,
            extra_data={
                key: self.to_dict(),
            },
        )

    @classmethod
    @beartype.beartype
    def from_agent_item(cls, item: "agent_model.AgentItem") -> "ConsulWatchCheckItem":
        key = "consul_watch_check_item"
        if key in item.extra_data:
            return cls(**item.extra_data[key])

        raise NotImplementedError()
        return cls(
            node="",
            check_id="",
            name="",
            status="",
            notes="",
            output="",
            service_id="",
            service_name="",
        )


@beartype.beartype
@dataclasses.dataclass
class ConsulHealthCheckStateItem(
    agent_model.ExternalItem, agent_model.AgentItemConvertMixin
):
    """A consul health check state item."""

    # Docs: https://www.consul.io/api-docs/health#list-checks-in-state
    # Endpoint: /health/state/:state

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
    service_tags: typing.List[str]  # consul: tags applied to the service
    namespace: typing.Optional[str] = None  # consul: enterprise-only namespace

    # {
    #         "Node": "test-wsu-blue.redboxresearchdata.com.au",
    #         "CheckID": "system-mem-usage-check",
    #         "Name": "system-mem-usage-check",
    #         "Status": "passing",
    #         "Notes": "This health check runs a script that checks for instance's memory usage.",
    #         "Output": "[2022-08-23 17:00:56 +1000] [INFO] [usage-mem.sh] Memory available: 68% (available); 72% (free + buff/cache)\n[2022-08-23 17:00:56 +1000] [INFO] [usage-mem.sh] Memory used: 32%\n[2022-08-23 17:00:56 +1000] [INFO] [usage-mem.sh] Memory usage normal (threshold 15):\n              total        used        free      shared  buff/cache   available\nMem:           7.5G        2.1G        481M         13M        4.9G        5.1G\nSwap:            0B          0B          0B\n",
    #         "ServiceID": "",
    #         "ServiceName": "",
    #         "ServiceTags": [],
    #         "Type": "",
    #         "Definition": {
    #             "Interval": "0s",
    #             "Timeout": "0s",
    #             "DeregisterCriticalServiceAfter": "0s",
    #             "HTTP": "",
    #             "Header": null,
    #             "Method": "",
    #             "Body": "",
    #             "TLSServerName": "",
    #             "TLSSkipVerify": false,
    #             "TCP": "",
    #             "GRPC": "",
    #             "GRPCUseTLS": false
    #         },
    #         "CreateIndex": 15246266,
    #         "ModifyIndex": 19970059
    #     }

    #  {
    #         "Node": "aws-prod-qcifeng-consul-02",
    #         "CheckID": "apt-auto-update-check-last-run",
    #         "Name": "apt-auto-update-check-last-run",
    #         "Status": "passing",
    #         "Notes": "Information about the need for a restart and most recent update run.",
    #         "Output": "File exists '/var/run/reboot-required':\n*** System restart required ***\n\nFile exists '/var/run/reboot-required.pkgs':\nlinux-image-5.13.0-1028-aws\nlinux-base\nlinux-image-5.13.0-1029-aws\nlinux-base\nlinux-image-5.13.0-1031-aws\nlinux-base\nlibssl1.1\nlibssl1.1\nlinux-image-5.15.0-1015-aws\nlinux-base\nlinux-image-5.15.0-1017-aws\nlinux-base\n\nFile exists '/var/lib/apt/periodic/unattended-upgrades-stamp':\n2022-08-23 06:47:53.459392248 +1000\n\nFile exists '/var/lib/apt/periodic/update-success-stamp':\n2022-08-23 02:59:38.173098693 +1000\n",
    #         "ServiceID": "apt-auto-update",
    #         "ServiceName": "apt-auto-update",
    #         "ServiceTags": [
    #             "application",
    #             "security"
    #         ],
    #         "Type": "script",
    #         "Definition": {
    #             "Interval": "0s",
    #             "Timeout": "0s",
    #             "DeregisterCriticalServiceAfter": "0s",
    #             "HTTP": "",
    #             "Header": null,
    #             "Method": "",
    #             "Body": "",
    #             "TLSServerName": "",
    #             "TLSSkipVerify": false,
    #             "TCP": "",
    #             "GRPC": "",
    #             "GRPCUseTLS": false
    #         },
    #         "CreateIndex": 16866146,
    #         "ModifyIndex": 19952627
    #     },

    @classmethod
    def data_type_name(cls):
        return "consul-health-check-state"

    @beartype.beartype
    def to_dict(self) -> typing.Dict:
        return {
            "Node": self.node,
            "CheckID": self.check_id,
            "Name": self.name,
            "Status": self.status,
            "Notes": self.notes,
            "Output": self.output,
            "ServiceID": self.service_id,
            "ServiceName": self.service_name,
            "ServiceTags": self.service_tags,
            "Namespace": self.namespace,
        }

    @classmethod
    @beartype.beartype
    def from_dict(cls, item: typing.Dict) -> "ConsulHealthCheckStateItem":
        return ConsulHealthCheckStateItem(
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

    @beartype.beartype
    def to_agent_item(self) -> "agent_model.AgentItem":
        key = "consul_watch_check_item"

        raise NotImplementedError()
        summary = ""
        description = ""
        source_name = ""
        check_name = ""
        date = ""
        status_name = ""
        return agent_model.AgentItem(
            summary=summary,
            description=description,
            host_name=self.node,
            source_name=source_name,
            check_name=check_name,
            date=date,
            status_name=status_name,
            service_name=self.service_name,
            extra_data={
                key: self.to_dict(),
            },
        )

    @classmethod
    @beartype.beartype
    def from_agent_item(
        cls, item: "agent_model.AgentItem"
    ) -> "ConsulHealthCheckStateItem":
        key = "consul_health_check_state_item"
        if key in item.extra_data:
            return cls(**item.extra_data[key])

        raise NotImplementedError()
        return cls(
            node="",
            check_id="",
            name="",
            status="",
            notes="",
            output="",
            service_id="",
            service_name="",
            service_tags=[],
            namespace="",
        )


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
