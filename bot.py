import socket
import random
import sys
import string
import client

class Bot(client.Client):
    """An implementation of Client as a bot to perform commands from users at runtime."""

    def __init__(self):
        super().__init__()

    def connect_to_server(self):
        self.username = "IRCBot"

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.client_socket.setblocking(False)

        username_encoded = self.username.encode(self.encoding_scheme)
        username_header = f"{len(self.username):<{self.header_length}}".encode(self.encoding_scheme)
        self.client_socket.send(username_header + username_encoded)

    def listen(self):
        pass

    def check_for_command(self):
        pass

    def reply(self):
        pass

    def parse_server_data(self):
        pass

print("This is the bot file.")

if __name__ == "__main__":
    bot = Bot()
    bot.client_test_method()
    bot.bot_test_method()