# import socketserver
from http import server


class EchoHTTPRequestHandler(server.BaseHTTPRequestHandler):
    pass


# ADDR = "127.0.0.1"
# PORT = 8000
# Handler = EchoHTTPRequestHandler
# with socketserver.TCPServer((ADDR, PORT), Handler) as httpd:
#     print("serving at port", PORT)
#     httpd.serve_forever()
