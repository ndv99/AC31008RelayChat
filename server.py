import select
import socket
import sys
import types
import threading
from connection import Connection
from server_mem import Memory


class Server:
    """A generic IRC server.
    """

    def __init__(self, ipv6_addr="::1"):
        """Initialises a Server object.

        Args:
            ipv6_addr (str, optional): A calid IPv6 address on which to host the server. Defaults to "::1".
        """        

        self.memory = Memory(ipv6_addr)

    def start_server(self):
        """Starts the server."""

        self.memory.socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Socket options
        # Bind a socket to a given IP and port
        self.memory.socket.bind((self.memory.ipv6_address, self.memory.port))

        print(
            f"'{self.memory.server_name}' is now running on {self.memory.ipv6_address}:{self.memory.port}.")

    def event_loop(self):
        """Event loop for the server, listens for new connections and accepts them."""

        self.memory.socket.listen()

        while True:

            # Accept a connection from a new client and assigns them a unique socket
            client_sckt, client_addr = self.memory.socket.accept()

            conn = Connection(client_sckt, client_addr, self.memory)
            threading.Thread(target=conn.loop).start()


def process_args(arg):
    """Processes the arguments provided in the terminal.

    Args:
        arg (string): Should be an IPv6 address

    Returns:
        bool: True if address is valid, false if address is invalid.
    """

    try:
        socket.inet_pton(socket.AF_INET6, arg)
        return True
    except socket.error:
        print(
            "That IP address is not valid. Please provde a valid IP adddress and try again.")
        return False


if __name__ == "__main__":
    try:
        valid = process_args(sys.argv[1])
        if valid:
            server = Server(ipv6_addr=sys.argv[1])
        else:
            sys.exit(1)
    except IndexError:
        print("No args given, using default IPv6 address (::1)")
        server = Server()
    server.start_server()
    server.event_loop()
