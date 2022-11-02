"""The command line entry module."""

import logging
import sys

from server_monitor_agent.agent import cli, common


def main() -> None:
    """The main function for running as a command line program."""

    logging.basicConfig(
        format="%(asctime)s [%(levelname)-8s]  %(message)s",
        datefmt="%a %d %b %H:%M:%S",
        level=logging.INFO,
    )
    if "--debug" in sys.argv:
        logging.getLogger().setLevel(logging.DEBUG)

    cli_parser = cli.build()

    args = cli_parser.parse_args()

    if args.debug:
        result: common.CheckReport = args.func(args)

    else:
        try:
            result: common.CheckReport = args.func(args)
        except Exception as e:
            print(
                f"Error running check '{args.subparser_name}' - "
                f"'{e.__class__.__name__}': \"{str(e)}\"",
                file=sys.stderr,
            )
            sys.exit(1)

    if result.exit_code == 0:
        print(result.content, file=sys.stdout)
    else:
        print(result.content, file=sys.stderr)
        sys.exit(result.exit_code)


if __name__ == "__main__":
    main()
