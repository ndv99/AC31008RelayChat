import socket
import random
import sys
import string

class Bot():
    """An implementation of Client as a bot to perform commands from users at runtime."""

    def __init__(self):
        self.socket = None
        self.nickname = "IRCBot"
        self.realname = "IRCBot"
        self.host = "::1"
        self.port = 6667

        self.channels = []

    def connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.send_message(f"NICK {self.nickname}")
        self.send_message(f"USER {self.realname} 0 * :realname")
        self.get_channels()
        self.join_channels()
    
    def get_channels(self):
        self.send_message(f"LIST")
        list_end = False
        messages = []
        
        while not list_end:
            msg = self.socket.recv(4096)
            if msg:
                msg = msg.decode().split(" ")
                messages.append(msg)
                if msg[1] == "323":
                    list_end = True

        for message in messages:
            if message[1] == '322':
                self.channels.append(message[3])
    
    def join_channels(self):
        for channel in self.channels:
            self.send_message(f"JOIN {channel}")

    def listen(self):
        while True:
            msg = self.socket.recv(4096)
            if msg:
                print(msg.decode())

    def check_for_command(self):
        pass

    def reply(self):
        pass

    def send_message(self, msg):
        self.socket.send(f"{msg}\r\n".encode())

    def parse_server_data(self):
        pass


if __name__ == "__main__":
    bot = Bot()
    bot.connect_to_server()
    bot.listen()