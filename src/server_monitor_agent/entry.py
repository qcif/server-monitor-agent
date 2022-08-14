"""The command line entry module."""

import logging
import sys

from server_monitor_agent.agent import command
from server_monitor_agent.agent.register import Registry


def main() -> None:
    """The main function for running as a command line program."""

    logging.basicConfig(
        format="%(asctime)s [%(levelname)-8s]  %(message)s",
        datefmt="%a %d %b %H:%M:%S",
        level=logging.INFO,
    )
    if "--debug" in sys.argv:
        logging.getLogger().setLevel(logging.DEBUG)

    reg = Registry()
    reg.gather_services()

    command.cli()


if __name__ == "__main__":
    main()
