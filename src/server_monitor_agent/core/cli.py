"""Module for building cli."""


import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from server_monitor_agent.common import ReportMixin, LoggingMixin, RunArgs
from server_monitor_agent.core.manage import Manager

CustomSubParserAction = argparse._SubParsersAction


class Cli(LoggingMixin):
    """Build and run a command line interface."""

    name = "server-monitor-agent"

    description = "Run checks on a server and send formatted notifications."

    _logger: logging.Logger = logging.getLogger(name)

    _msg_exclusive = "Mutually exclusive with other output options."
    _msg_name_where = "either built-in or defined in the config file"
    _msg_error_help = "Run with '--log-level=debug' for more information."

    def __init__(self):
        from colorama import init

        init()

        self._parser = self.build()

    @property
    def version(self) -> Optional[str]:
        from importlib import metadata

        try:
            return metadata.version(self.name)
        except metadata.PackageNotFoundError:
            return None

    def build(self) -> argparse.ArgumentParser:
        """Build the arguments for the main command."""

        parser = argparse.ArgumentParser(
            prog=self.name,
            description=self.description,
            exit_on_error=False,
        )
        parser.add_argument(
            "-v", "--version", action="version", version=self.version or ""
        )
        self._add_log_level(parser)
        parser.set_defaults(func=self.run_main)

        sub_parser = self.build_sub(parser)
        self.build_check(sub_parser)
        self.build_notify(sub_parser)
        self.build_list(sub_parser)
        return parser

    def build_sub(self, parser: argparse.ArgumentParser) -> CustomSubParserAction:
        """Build the sub commands."""

        sub_parser = parser.add_subparsers(
            title="Available commands",
            description="Select a sub-command to run.",
            help="The sub-command.",
            required=False,
            dest="sub_command_name",
            metavar="{sub_command}",
        )
        return sub_parser

    def build_check(self, sub_parser: CustomSubParserAction) -> argparse.ArgumentParser:
        """Build the arguments for the check command."""
        descr = (
            "Gather information about the instance and "
            "report the result via exit code and json-formatted output."
        )
        parser = sub_parser.add_parser("check", help=descr, description=descr)
        parser.add_argument(
            "name",
            help=f"The check name, {self._msg_name_where}.",
        )
        parser.add_argument(
            "--format",
            choices=["agent"],
            default="agent",
            help="The format of the output. Default is agent json format.",
        )

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--std-out",
            action="store_true",
            help=f"Send the output to standard out. {self._msg_exclusive}",
        )
        group.add_argument(
            "--std-err",
            action="store_true",
            help=f"Send the output to standard error. {self._msg_exclusive}",
        )
        group.add_argument(
            "--write-file",
            help=f"Send the output to the given file path. {self._msg_exclusive}",
        )
        self._add_log_level(parser)
        self._add_config(parser)
        parser.set_defaults(func=self.run_check)
        return parser

    def build_notify(
        self, sub_parser: CustomSubParserAction
    ) -> argparse.ArgumentParser:
        """Build the arguments for the notify command."""

        descr = (
            "Send a message to an alerting service. "
            "One message contains output from one or more checks."
        )
        parser = sub_parser.add_parser("notify", help=descr, description=descr)
        parser.add_argument(
            "name",
            help="The notification service name, "
            "either built-in or defined in the config file.",
        )
        parser.add_argument(
            "--format",
            choices=["agent", "consul-watch"],
            default="agent",
            help="The format of the output. Default is agent json format.",
        )
        parser.add_argument(
            "--level",
            choices=ReportMixin.report_choices(),
            help="The notification level when not specified in the input content.",
        )

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--std-in",
            action="store_true",
            help=f"Get the output from standard in. {self._msg_exclusive}",
        )
        group.add_argument(
            "--read-file",
            help=f"Get the input from the given file path. {self._msg_exclusive}",
        )
        self._add_log_level(parser)
        self._add_config(parser)
        parser.set_defaults(func=self.run_notify)
        return parser

    def build_list(self, sub_parser: CustomSubParserAction) -> argparse.ArgumentParser:
        """Build the list command."""

        descr = "List all the check and notify entries."
        parser = sub_parser.add_parser("list", help=descr, description=descr)
        self._add_log_level(parser)
        self._add_config(parser)
        parser.set_defaults(func=self.run_list)
        return parser

    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the program with the given args."""

        if args is None:
            args = sys.argv[1:]

        # print the help and exit if no arguments provided
        if len(args) < 1:
            self._parser.print_help(sys.stderr)
            return 0

        try:
            self._logger.debug("Running parser with args.")
            parsed_args = self._parser.parse_args(args)
        except argparse.ArgumentError as e:
            self._logger.error(
                f"Command failed: Argument error: '{str(e)}'."
                f"  {self._msg_error_help}"
            )
            return 1
        except argparse.ArgumentTypeError as e:
            self._logger.error(
                f"Command failed: Argument type error: '{str(e)}'."
                f"  {self._msg_error_help}"
            )
            return 1

        # set logging level
        log_level = (
            parsed_args.log_level
            if parsed_args and hasattr(parsed_args, "log_level")
            else None
        )
        if log_level and log_level in self.logging_choices():
            logging.root.setLevel(self.logging_value(log_level))

        # run command
        success, detail = self._run_command(args, parsed_args)
        return 0 if success else 1

    def run_main(self, args: argparse.Namespace) -> tuple[bool, Optional[str]]:
        """Run the main command."""

        self._logger.warning(f"Not implemented '{args}'.")
        return False, None

    def run_check(self, args: argparse.Namespace):
        """Run the check command."""
        self._run_func(
            RunArgs(
                group="check",
                name=args.name,
                level=None,
                fmt=args.format,
                std_io=args.std_out,
                std_err=args.std_err,
                file_path=args.write_file,
            ),
            config_path=args.config,
        )

    def run_notify(self, args: argparse.Namespace):
        """Run the notify command."""
        self._run_func(
            RunArgs(
                group="notify",
                name=args.name,
                level=args.level,
                fmt=args.format,
                std_io=args.std_in,
                std_err=False,
                file_path=args.read_file,
            ),
            config_path=args.config,
        )

    def run_list(self, args: argparse.Namespace):
        self._run_func(
            RunArgs(
                group="list",
                name=None,
                level=None,
                fmt=None,
                std_io=True,
                std_err=False,
                file_path=None,
            ),
            config_path=args.config,
        )

    def _add_log_level(self, p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--log-level",
            choices=LoggingMixin.logging_choices(),
            default="info",
            help="Set the log level. Default is info.",
        )

    def _add_config(self, p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--config",
            type=Path,
            default=".server-monitor-agent.yml",
            help="Specify the path to the config file. "
            "Default is ./.server-monitor-agent.yml",
        )

    def _run_func(self, run_args: RunArgs, config_path: Path):
        manager = Manager()
        manager.process(run_args, config_path)

    def _run_command(self, args, parsed_args):
        detail: Optional[str] = None

        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(f"Starting {self.name} in debug mode.")
            self._logger.debug(f"Raw arguments: {' '.join(args)}")
            self._logger.debug(f"Parsed arguments: {parsed_args}")

            parsed_args.func(parsed_args)
            success = True

            self._logger.debug("Finished parser func with parsed args in debug mode.")

        else:
            try:
                parsed_args.func(parsed_args)
                success = True

            except Exception as e:
                success = False
                detail = f"{type(e).__name__}: {str(e)}"

            except SystemExit as e:
                success = e.code == 0
                detail = str(e)

        # record outcome
        outcome = "succeeded" if success else "failed"
        if success and detail:
            self._logger.info(f"Command {outcome}: {detail}")

        elif not success:
            from colorama import Fore, Style

            if detail:
                self._logger.error(
                    f"{Fore.RED}Command {outcome}: {detail}{Style.RESET_ALL}"
                )
            else:
                self._logger.error(f"{Fore.RED}Command {outcome}{Style.RESET_ALL}")

            self._logger.info(self._msg_error_help)

        return success, detail
