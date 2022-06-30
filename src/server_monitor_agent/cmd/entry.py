"""The command line entry module."""


import logging
import sys
from typing import Optional, List

from server_monitor_agent.cmd.cli import Cli

logging.basicConfig(
    format="%(asctime)s [%(levelname)-8s]  %(message)s",
    datefmt="%a %d %b %H:%M:%S",
    level=logging.INFO,
)


def main(args: Optional[List[str]] = None) -> int:
    cli = Cli()
    return cli.run(args)


if __name__ == "__main__":
    sys.exit(main())
