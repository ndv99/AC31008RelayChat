import socket
import random
import sys
import string
import datetime
import puns

class Bot():
    """An implementation of Client as a bot to perform commands from users at runtime."""

    def __init__(self, ipv6_addr="::1"):
        self.socket = None
        self.nickname = "IRCBot"
        self.second_choice = "RealBot"
        self.realname = "IRCBot"
        self.host = ipv6_addr
        self.port = 6667

        self.channels = []

    def connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print("connected")
        self.send_message(f"NICK {self.nickname}")
        self.send_message(f"USER {self.realname} 0 * :realname")
        print("sent nick and user")
        self.check_nickname()
        self.get_channels()
        self.join_channels()
    
    def check_nickname(self):
        list_end = False
        messages = []

        attempts = 1
        while not list_end:
            msg = self.socket.recv(4096)
            if msg:
                msg = msg.decode().split('\r\n')
                for part in msg:
                    if part:
                        if part.split(" ")[1] == '432' or part.split(" ")[1] == '433':
                            if attempts == 1:
                                self.nickname = self.second_choice
                                self.send_message(f"NICK {self.nickname}")
                                attempts += 1
                            else:
                                print("Built-in nickname options exhausted. Enter a different nickname in self.nickname.")
                                sys.exit(0)
                        elif part.split(" ")[1] == "001":
                            list_end = True

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
            print(message)
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
                            if msg[1] == "PRIVMSG":
                                if msg[2] in self.channels:
                                    if msg[3][1] == "!":
                                        nickname = msg[0].split("!")[0][1:]
                                        self.process_message(msg[2], msg[3], nickname)
                                else:
                                    pun = puns.puns[random.randint(0, len(puns.puns)-1)]
                                    nickname = msg[0].split("!")[0][1:]
                                    self.send_privmsg(nickname, pun)

        except ConnectionResetError:
            print("The server has closed. Shutting down bot.")
            sys.exit(0)

    def process_message(self, chan, msg, nick):
        msg = msg.strip()

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

    def send_message(self, msg):
        self.socket.send(f"{msg}\r\n".encode())

    def send_privmsg(self, target, msg):
        self.socket.send(f"PRIVMSG {target} :{msg}\r\n".encode())

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
            bot = Bot(sys.argv[1])
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
