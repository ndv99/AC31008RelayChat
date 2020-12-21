class Connection:
    """A connection to the IRC server in server.py.

    Args:
        sckt - A socket object
        addr - The address that the connection is coming from
        mem - A server memory object (from server_mem.py)
    """

    def __init__(self, sckt, addr, mem):
        """Initialises a client object

        Args:
            sckt (socket.Socket): A socket object of the new connection.
            addr (str): The IP address of the new connection (IPv6) and the port (6667 for IRC).
            mem (server_mem.Memory): An object containing the server memory.
        """

        self.socket = sckt
        self.address = addr[0]
        self.nickname = ""
        self.realname = ""

        self.nick_set = False  # tracks if the nickname has been set for the first time

        self.server_mem = mem

        # list of recognised commands
        self.commands = [
            "CAP",
            "NICK",
            "USER",
            "QUIT",
            "JOIN",
            "PART",
            "PRIVMSG",
            "WHO",
            "MODE",
            "LIST"
        ]

        # used for caching the USER command when the intial nickname selection fails (invalid nickname)
        self.cached_command = None

    def loop(self):
        """The main event loop for the connection.
        """

        try:
            while True:
                msg = self.socket.recv(4096)
                if msg:
                    # splits the messages up (they're separated by \r\n)
                    msg = msg.decode().split('\r\n')

                    for part in msg:
                        if part:
                            self.check_command(part)

                    # So this little bit of code is basically to cache the USER command until the nickname has been verified for the first time.
                    if self.cached_command is not None:
                        self.check_command(None, self.cached_command)
        except ConnectionResetError:  # this happens when a client disconnects.
            print("Client disconnected. Connection reset.")
            if self.socket in self.server_mem.clients:
                del self.server_mem.clients[self.socket]

        # no idea when this happens but I know that it can so better catch it just in case.
        except BrokenPipeError:
            print("Broken pipe (how the fuck did this happen?!)")

    def check_command(self, cmd_string, cmd_split=None):
        """Checks a command sent from a client

        Args:
            cmd_string (string): A command given as a string (default)
            cmd_split (list, optional): Effectively cmd_string but split by a space. Defaults to None. Only needed for cached commands.
        """

        if cmd_split is not None:
            cmd = cmd_split
        else:
            cmd = cmd_string.split(" ")
        print(f"Running command: {' '.join(cmd)}")

        if cmd[0] in self.commands:
            if cmd[0] == "NICK":
                self.set_nickname(cmd[1])
            elif cmd[0] == "USER":
                if self.nick_set:
                    self.set_realname(cmd[1])
                    # gotta uncache it if it's been cached.
                    self.cached_command = None
                else:
                    self.cached_command = cmd
            elif cmd[0] == "QUIT":
                del self.server_mem.clients[self.socket]
            elif cmd[0] == "JOIN":
                self.join_channel(cmd[1])
            elif cmd[0] == "PRIVMSG":
                self.message(cmd[1], " ".join(cmd[2:]))
            elif cmd[0] == "PART":
                self.leave_channel(cmd[1])
            elif cmd[0] == "LIST":
                self.list_channels()
        else:
            # not needed for hexchat since it handles that client-side but it's good to have for when ludovic tests this with socat.
            # any commands that hexchat sends that I don't deal with are just added to self.commands.
            print(f"Received unknown command: {cmd}.")
            self.send_code("421", cmd[0], ":Unknown command")

    def set_nickname(self, nickname):
        """Attempts to set a new nickname specified by the cient.

        Args:
            nickname (string): The nickname that the cient is attempting to use.

        Returns:
            bool: True if successful, False if not.
        """

        # this is just all IRC spec basics
        if len(nickname) > 9 or nickname[0] == "-" or nickname[0] == "#":
            print("Client tried to connect with invalid username")
            code = "432"
            msg = f":{nickname}"
            self.send_code(code, nickname, msg)
            return False

        try:
            if int(nickname[0]):
                print("Client tried to connect with invalid username")
                code = "432"
                msg = f":{nickname}"
                self.send_code(code, nickname, msg)
                return False
        except ValueError:
            pass

        for client in self.server_mem.clients:
            if self.server_mem.clients[client] == nickname:
                print("Client tried to connect with taken username")
                code = "433"
                msg = f":{nickname}"
                self.send_code(code, nickname, msg)
                return False

        self.nickname = nickname
        self.nick_set = True

        msg = f"NICK {nickname}"
        self.send_message_from_server(msg)
        self.server_mem.clients[self.socket] = self.nickname
        return True

    def set_realname(self, name):
        """Sets the real name (username) of the client. Welcomes the client since username can only be set upon login.

        Args:
            name (string): The new username to be set.
        """

        self.realname = name

        self.server_mem.clients[self.socket] = self.nickname
        self.send_welcome_messages()  # separated this for atomicity.

    def send_welcome_messages(self):
        """Sends welcome messages to the user.
        """

        msg = f"Welcome to the Internet Relay Network {self.nickname}!{self.nickname}@{self.address}"
        self.send_code("001", self.nickname, msg)

        msg = f"Your host is {self.server_mem.ipv6_address}, running version {self.server_mem.server_name}"
        self.send_code("002", self.nickname, msg)

        msg = f"This server was created in 2000 - no wait, that's the protocol. The server was made 20 years after everyone stopped using IRC."
        self.send_code("003", self.nickname, msg)

        msg = f"{self.server_mem.server_name} v{self.server_mem.server_version}"
        self.send_code("004", self.nickname, msg)

    def list_channels(self):
        """Sends a list of channels back to the client.
        """
        for channel in self.server_mem.channels:
            msg = f"{channel} {len(self.server_mem.channels[channel])} :"
            self.send_code("322", self.nickname, msg)
        msg = f":End of /LIST"
        self.send_code("323", self.nickname, msg)

    def join_channel(self, chan):
        """Puts the client into a channel that they have specified.

        Args:
            chan (string): The name of the channel.
        """

        # creates the requested channel if it doesn't exist (for some reason)
        if chan not in self.server_mem.channels:
            self.server_mem.channels[chan] = []

        self.server_mem.channels[chan].append(self.socket)
        for socket in self.server_mem.channels[chan]:
            msg = f"{self.nickname}!{self.realname}@{self.address} JOIN {chan}"
            self.send_message(socket, msg)

        # none of the channels have a topic leave me alone
        msg = f"332 {chan} :{chan} no topic"
        self.send_message_from_server(msg)

        chan_members = []
        for socket in self.server_mem.channels[chan]:
            chan_members.append(self.server_mem.clients[socket])
        chan_members = " ".join(chan_members)
        msg = f"= {chan} :{chan_members}"
        code = "353"
        self.send_code(code, self.nickname, msg)

        msg = ":End of NAMES list"
        code = "366"
        self.send_code(code, chan, msg)

    def leave_channel(self, chan):
        """Removes a client from a channel.

        Args:
            chan (string): The name of the channel.
        """

        if chan in self.server_mem.channels:
            if self.socket in self.server_mem.channels[chan]:
                self.server_mem.channels[chan].remove(self.socket)
                for socket in self.server_mem.channels[chan]:
                    msg = f"{self.nickname}!{self.realname}@{self.address} PART {chan}"
                    self.send_message(socket, msg)
            else:
                msg = ":You're not on that channel."
                self.send_code("442", chan, msg)
        else:
            msg = ":No such channel."
            self.send_code("403", chan, msg)

    def message(self, chan, msg):
        """Sends a message from a user to a channel or another user.

        Args:
            chan (string): The name of the channel/user to send to.
            msg (string): The message to be sent.
        """

        if chan[0] == "#":  # if target is a channel
            for client in self.server_mem.channels[chan]:
                if client != self.socket:
                    self.send_privmsg(client, msg, chan)
        else:  # if target is a user
            for client in self.server_mem.clients:
                if self.server_mem.clients[client] == chan:
                    self.send_privmsg(client, msg, chan)

    def send_code(self, code, subj, msg):
        """Sends a numeric reply code code to the client from the server.

        Args:
            code (string): The code to be sent (numeric, see IRC documentation https://tools.ietf.org/html/rfc1459)
            subj (string): The subject of the code (user, command, channel etc.)
            msg (string): Any additional text to be sent after the code.
        """

        self.socket.send(
            f":{self.server_mem.ipv6_address} {code} {subj} {msg}\r\n".encode())
        print(f":{self.server_mem.ipv6_address} {code} {subj} {msg}\r\n")

    def send_message_from_server(self, msg):
        """Sends a message from the server to the client.

        Args:
            msg (string): The message to be sent.
        """

        self.socket.send(f":{self.server_mem.ipv6_address} {msg}\r\n".encode())
        print(f":{self.server_mem.ipv6_address} {msg}\r\n")

    def send_privmsg(self, sckt, msg, chan):
        """Sends a message from the client to another user.

        Args:
            sckt (socket.Socket): The recipient's socket.
            msg (string): The message to be sent.
            chan (string): The target channel of the message (either a username or a channel name).
        """

        sckt.send(
            f":{self.nickname}!{self.realname}@{self.address} PRIVMSG {chan} {msg}\r\n".encode())
        print(
            f"from {self.nickname} to {chan}:{self.nickname}!{self.realname}@{self.address} PRIVMSG {chan} {msg}")

    def send_message(self, sckt, msg):
        """Sends a message from this socket to another socket. Mainly for debugging.

        Args:
            sckt (socket.Socket): The recipient's socket.
            msg (string): The message to be sent.
        """

        sckt.send(f":{msg}\r\n".encode())
        print(f"sent this:{msg}\r\n")
