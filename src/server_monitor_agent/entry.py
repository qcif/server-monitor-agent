"""The command line entry module."""

import logging
import sys
import typing

from server_monitor_agent.agent import cli, common


def main(args: typing.Optional[typing.List[str]] = None) -> int:
    """Run as a command line program.

    Args:
        args: The program arguments.
    Returns:
        int: Program exit code.
    """
    if args is None:
        args = sys.argv[1:]

    logging.basicConfig(
        format="%(asctime)s [%(levelname)-8s]  %(message)s",
        datefmt="%a %d %b %H:%M:%S",
        level=logging.INFO,
    )
    if "--debug" in sys.argv:
        logging.getLogger().setLevel(logging.DEBUG)

    cli_parser = cli.build()

    args = cli_parser.parse_args(args)

    if not hasattr(args, "func"):
        cli_parser.print_help(file=sys.stderr)
        return 1

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
            # Exit code 1 is treated as 'warning' by consul.
            return 1

    if result.exit_code == 0:
        print(result.content, file=sys.stdout)
    else:
        print(result.content, file=sys.stderr)

    return result.exit_code


if __name__ == "__main__":
    # python convention is to call sys.exit
    # only if this file is run as the 'top-level code environment'.
    sys.exit(main())
