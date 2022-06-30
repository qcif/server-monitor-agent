import platform
import socket


class Instance:
    @property
    def hostname(self) -> str:
        hostname = ""

        if not hostname:
            hostname = socket.getfqdn()

        if not hostname:
            hostname = platform.node()

        return hostname
