import socket
import random
import sys
import string
import datetime
import puns

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
                msg = msg.decode().split('\r\n')
                for part in msg:
                    if part:
                        messages.append(part.split(" "))
                        if part.split(" ")[1] == "323":
                            list_end = True

        for message in messages:
            if message[1] == '322':
                self.channels.append(message[3])
    
    def join_channels(self):
        for channel in self.channels:
            self.send_message(f"JOIN {channel}")
        self.send_message(f"PRIVMSG #test :Hello everyone!")

    def listen(self):
        try:
            while True:
                data = self.socket.recv(4096)
                if data:
                    print(data.decode())
    
                    parts = data.decode().split('\r\n')
                    for part in parts:
                        msg = part.split(" ")
                        print(msg)
                        if len(msg) > 3:
                            print(f"msg[2]: {msg[2]}")
                            print(f"Channels: {self.channels}")
                            if msg[2] in self.channels:
                                print("Channel is in channels")
                                print(f"Message: {msg[3]}")
                                if msg[3][1] == "!":
                                    nickname = msg[0].split("!")[0][1:]
                                    self.process_message(msg[2], msg[3], nickname)
                                else  
                                    pun = puns.puns[random.randint(0, len(puns.puns)-1)]
                                    self.send_privmsg(msg[2], pun)
        except ConnectionResetError:
            print("The server has closed. Shutting down bot.")
            sys.exit(0)

    def process_message(self, chan, msg, nick):
        msg = msg.strip()
        print(chan.encode())

        if msg == ":!slap":
            self.slap(chan)
        elif msg == ":!hello":
            now = datetime.datetime.now()
            message = f"Hello {nick}, the date and time is {now.strftime('%Y-%m-%d %H:%M:%S')}"
            self.send_privmsg(chan, message)
   
    def slap(self, chan):
        nicks = self.get_nicks(chan)
        to_slap = random.randint(0, len(nicks)-1)
        print("Slapping user")
        self.send_privmsg(chan, f"Oi. {nicks[to_slap]}. https://youtu.be/dtxPp9UOcIc")

    def get_nicks(self, chan):
        self.send_message(f"NAMES {chan}")
        list_end = False
        messages = []
        
        while not list_end:
            msg = self.socket.recv(4096)
            if msg:
                msg = msg.decode().split('\r\n')
                for part in msg:
                    if part:
                        messages.append(part.split(" "))
                        if part.split(" ")[1] == "366":
                            list_end = True
        nicknames = []

        for message in messages:
            if message[1] == '353':
                message[5] = message[5][1:]
                nicknames = (message[5:])
        return nicknames

    def check_for_command(self):
        pass

    def reply(self):
        pass

    def send_message(self, msg):
        self.socket.send(f"{msg}\r\n".encode())

    def send_privmsg(self, target, msg):
        self.socket.send(f"PRIVMSG {target} :{msg}\r\n".encode())

    def parse_server_data(self):
        pass

def process_args(arg):
    """Processes the arguments provided in the terminal.

    Args:
        arg (string): Should be an IPv6 address

    Returns:
        bool: True if address is valid, false if address is invalid.
    """

    try:
        socket.inet_aton(arg)
        return True
    except socket.error:
        print(
            "That IP address is not valid. Please provde a valid IP adddress and try again.")
        return False


if __name__ == "__main__":
    try:
        valid = process_args(sys.argv[1])
        if valid:
            bot = Bot()
        else:
            sys.exit(1)
    except IndexError:
        print("No args given, connecting to default IPv6 address (::1)...")
        bot = Bot()
    try:
        bot.connect_to_server()
        bot.listen()
    except ConnectionRefusedError:
        print("The server is not running. Contact the server owner.")
        sys.exit(1)
