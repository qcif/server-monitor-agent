"""The command line entry module."""

import logging

from server_monitor_agent.cli import command


def main() -> None:
    """The main function for running as a command line program."""

    logging.basicConfig(
        format="%(asctime)s [%(levelname)-8s]  %(message)s",
        datefmt="%a %d %b %H:%M:%S",
        level=logging.INFO,
    )
    command.cli()


if __name__ == "__main__":
    main()
