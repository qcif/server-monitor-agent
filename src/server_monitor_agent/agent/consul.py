import dataclasses
import json
import pathlib
import typing

import requests

from server_monitor_agent.agent import common


@dataclasses.dataclass
class ConsulConnection:
    http_ssl_enabled: bool = True
    http_ssl_verify: bool = True
    http_addr: str = "https://localhost:8501"
    data_centre: typing.Optional[str] = None
    ca_cert_file: typing.Optional[pathlib.Path] = None
    ca_cert_dir: typing.Optional[pathlib.Path] = None
    client_cert: typing.Optional[pathlib.Path] = None
    client_key: typing.Optional[pathlib.Path] = None

    @property
    def base_url(self):
        return f"{self.http_addr}/v1"

    def validate(self):
        if not self.http_addr:
            raise ValueError("Consul settings are invalid: must provide http_addr.")

        if self.http_ssl_enabled and not self.http_addr.startswith("https"):
            raise ValueError(
                "Consul settings are inconsistent: ssl is enabled but http_addr does not start with 'https'."
            )

        if not self.http_ssl_enabled and self.http_addr.startswith("https"):
            raise ValueError(
                "Consul settings are inconsistent: ssl is disabled but http_addr starts with 'https'."
            )

        if self.client_cert and not self.client_cert.exists():
            raise ValueError(
                f"Consul client cert file is specified but does not exist: {self.client_cert}."
            )

        if self.client_key and not self.client_key.exists():
            raise ValueError(
                f"Consul client key file is specified but does not exist: {self.client_key}."
            )

    def api(self, path: str) -> requests.Response:
        self.validate()

        if self.ca_cert_file and self.http_ssl_enabled:
            verify = str(self.ca_cert_file)
        else:
            verify = self.http_ssl_verify

        if self.client_cert and self.client_key:
            cert = (str(self.client_cert), str(self.client_key))
        else:
            cert = None

        try:
            req = requests.get(f"{self.base_url}/{path}", verify=verify, cert=cert)
        except requests.RequestException as e:
            raise ValueError(f"Consul http api {str(e)}") from e

        if req.status_code != 200:
            raise ValueError(f"Consul http api error {req.status_code}: {req.text}")

        return req

    def cli(self, args: typing.List[str]):
        self.validate()

        cmd_args = [
            "consul",
            *args,
            f"-http-addr={self.http_addr}",
        ]

        if self.client_cert and self.client_key:
            cmd_args.extend(
                [
                    f"-client-cert={str(self.client_cert)}",
                    f"-client-key={str(self.client_key)}",
                ]
            )

        if self.ca_cert_dir:
            cmd_args.append(f"-ca-path={str(self.ca_cert_dir)}")
        if self.ca_cert_file:
            cmd_args.append(f"-ca-file={str(self.ca_cert_file)}")
        if self.data_centre:
            cmd_args.append(f"-datacenter={self.data_centre}")

        result = common.execute_process(cmd_args)

        if result.returncode != 0 or result.stderr:
            raise ValueError(f"Consul cli error: {result}")

        return result


def consul_cli_watch_checks_any(conn: ConsulConnection) -> typing.List[typing.Dict]:
    args = [
        "watch",
        "-type=checks",
        "-state=any",
    ]
    result = conn.cli(args)
    return json.loads(result.stdout)


def consul_api_health_checks_any(conn: ConsulConnection) -> typing.List[typing.Dict]:
    req = conn.api(f"health/state/any")
    items = req.json()
    return items


def consul_api_status_leader(conn: ConsulConnection) -> str:
    req = conn.api("status/leader")
    return req.text.strip("\"' ")


def aws_instance_private_ipv4() -> str:
    # EC2 instance metadata IMDSv2
    # TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
    # Use 30 minutes instead = 1800 seconds
    token_headers = {"X-aws-ec2-metadata-token-ttl-seconds": "1800"}
    token_req = requests.put(url="http://169.254.169.254/latest/api/token", headers=token_headers)
    if token_req.status_code != 200:
        raise ValueError(f"AWS instance metadata token error {token_req.status_code}: {token_req.text}")

    # && curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/
    data_token = {"X-aws-ec2-metadata-token": token_req.text}
    data_req = requests.get(url="http://169.254.169.254/latest/meta-data/local-ipv4", headers=data_token)
    if data_req.status_code != 200:
        raise ValueError(f"AWS instance metadata data error {data_req.status_code}: {data_req.text}")

    return data_req.text
