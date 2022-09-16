import typing
from http import server

from tests.data import completed_process_examples as cp_eg


class EchoHTTPRequestHandler(server.BaseHTTPRequestHandler):
    pass


# ADDR = "127.0.0.1"
# PORT = 8000
# Handler = EchoHTTPRequestHandler
# with socketserver.TCPServer((ADDR, PORT), Handler) as httpd:
#     print("serving at port", PORT)
#     httpd.serve_forever()


def execute_process_side_effect(args: typing.Sequence[str]):
    match_any = "__MATCH_ANY__"
    for item in cp_eg.examples:

        if args == item.args:
            return item

        if match_any in item.args:
            match_any_index = item.args.index(match_any)
            args_without = args[:match_any_index] + args[match_any_index + 1 :]
            item_args_without = (
                item.args[:match_any_index] + item.args[match_any_index + 1 :]
            )
            if args_without == item_args_without:
                return item
    raise ValueError(f"Must handle args '{args}'.")
