import abc
import functools
import importlib
import inspect
import logging
from importlib import resources

import beartype
import click
from beartype import typing

from server_monitor_agent.agent import (
    model as agent_model,
    operation as agent_op,
)


class BaseRegistry(abc.ABC):
    @functools.cached_property
    @beartype.beartype
    def package_name(self) -> str:
        return agent_model.APP_NAME_UNDER

    @functools.cached_property
    @beartype.beartype
    def package_dir(self) -> importlib.abc.Traversable:
        return resources.files(self.package_name)

    @functools.cached_property
    @beartype.beartype
    def service_dir(self) -> importlib.abc.Traversable:
        return self.package_dir / "service"

    @beartype.beartype
    def service_module(self, service_name: str) -> str:
        return f"{self.package_name}.service.{service_name}"


class CommandRegistry(BaseRegistry):
    """Gathers and adds cli commands."""

    collect_commands: typing.List[agent_model.RegisterCollectCmd] = []
    send_commands: typing.List[agent_model.RegisterSendCmd] = []

    @beartype.beartype
    def collect_module(self, service_name: str) -> str:
        return f"{self.service_module(service_name)}.collect"

    @beartype.beartype
    def send_module(self, service_name: str) -> str:
        return f"{self.service_module(service_name)}.send"

    @beartype.beartype
    def gather(self):
        """Gather registered collect cli group commands and send commands."""

        for service in self.service_dir.iterdir():
            if service.name.startswith("_"):
                continue

            # collect commands
            collect_module = self.collect_module(service.name)
            for cmd in self.get_registered_commands(collect_module):
                if cmd not in self.collect_commands:
                    self.collect_commands.append(cmd)

            # send commands
            send_module = self.send_module(service.name)
            for cmd in self.get_registered_commands(send_module):
                if cmd not in self.send_commands:
                    self.send_commands.append(cmd)

    @beartype.beartype
    def run(self, group: click.Group):
        """Add registered collect commands to the given group.
        Add registered send commands to the collect groups."""

        for collect_cmd in self.collect_commands:

            agent_op.log_msg(
                logging.DEBUG, f"Register collect: cli -> {collect_cmd.group.name}."
            )
            group.add_command(collect_cmd.group)

            for send_cmd in self.send_commands:

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

    @beartype.beartype
    def get_registered_commands(
        self, module_name: str
    ) -> typing.Iterable[agent_model.RegisterCmd]:
        try:
            return importlib.import_module(module_name).register_commands
        except (ImportError, AttributeError):
            return []


class SourceTargetIORegistry(BaseRegistry):
    """Gather and link 'collect' source inputs and 'send' target outputs."""

    collect_inputs: typing.List[agent_model.RegisterCollectInput] = []
    send_outputs: typing.List[agent_model.RegisterSendOutput] = []

    @beartype.beartype
    def io_module(self, service_name: str) -> str:
        return f"{self.service_module(service_name)}.io"

    @beartype.beartype
    def gather(self):
        for service in self.service_dir.iterdir():
            if service.name.startswith("_"):
                continue

            io_module = self.io_module(service.name)
            for item in self.get_registered_sources_and_targets(io_module):
                if isinstance(item, agent_model.RegisterCollectInput):
                    if item not in self.collect_inputs:
                        self.collect_inputs.append(item)
                elif isinstance(item, agent_model.RegisterSendOutput):
                    if item not in self.send_outputs:
                        self.send_outputs.append(item)
                else:
                    raise ValueError(f"Unknown item: {repr(item)}")

    @beartype.beartype
    def run(
        self, collect_args: agent_model.CollectArgs, send_args: agent_model.SendArgs
    ) -> None:
        match_collect = None
        for item in self.collect_inputs:
            item_inspect = inspect.signature(item.func)
            item_arg_type = item_inspect.parameters["args"].annotation
            if item_arg_type == type(collect_args):
                match_collect = item
                break

        match_send = None
        for item in self.send_outputs:
            item_inspect = inspect.signature(item.func)
            item_arg_type = item_inspect.parameters["args"].annotation
            if item_arg_type == type(send_args):
                match_send = item
                break

        if not match_collect:
            raise ValueError(f"Unexpected collect args: {repr(collect_args)}")
        if not match_send:
            raise ValueError(f"Unexpected send args: {repr(send_args)}")

        agent_item = match_collect.func(collect_args)
        match_send.func(send_args, agent_item)

    @beartype.beartype
    def get_registered_sources_and_targets(
        self, module_name: str
    ) -> typing.Iterable[agent_model.RegisterCmd]:
        try:
            return importlib.import_module(module_name).register_io
        except (ImportError, AttributeError):
            return []
