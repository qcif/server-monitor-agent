import importlib
import logging
from importlib import resources

from beartype import typing

from server_monitor_agent.agent import (
    command as agent_command,
    model as agent_model,
    operation as agent_op,
)


class Registry:
    """Gathers and adds cli commands."""

    @property
    def base_module(self) -> str:
        return f"{agent_model.APP_NAME_UNDER}.service"

    def gather_services(self):
        package_name = agent_model.APP_NAME_UNDER
        package = resources.files(package_name)

        collect_commands: list[agent_model.RegisterCollectCmd] = []
        send_commands: list[agent_model.RegisterSendCmd] = []

        service_dir = package / "service"
        for service in service_dir.iterdir():
            if service.name.startswith("_"):
                continue

            service_base_name = f"{package_name}.service.{service.name}"
            service_collect_name = f"{service_base_name}.collect"
            collect_commands.extend(self.get_registered_commands(service_collect_name))

            service_send_name = f"{service_base_name}.send"
            send_commands.extend(self.get_registered_commands(service_send_name))

        for collect_cmd in collect_commands:

            agent_op.log_msg(
                logging.DEBUG, f"Register collect: cli -> {collect_cmd.group.name}."
            )
            agent_command.cli.add_command(collect_cmd.group)

            for send_cmd in send_commands:

                if (
                    not send_cmd.collect_only
                    or collect_cmd.group.name in send_cmd.collect_only
                ):
                    agent_op.log_msg(
                        logging.DEBUG,
                        f"Register send: {collect_cmd.group.name} "
                        f"-> {send_cmd.command.name}.",
                    )
                    collect_cmd.group.add_command(send_cmd.command)

    def get_registered_commands(
        self, name: str
    ) -> typing.Iterable[agent_model.RegisterCmd]:
        try:
            return importlib.import_module(name).register_commands
        except (ImportError, AttributeError):
            return []
