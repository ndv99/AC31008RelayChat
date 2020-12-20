class Connection:

    def __init__(self, sckt, addr, mem):
        self.socket = sckt
        self.address = addr[0]
        self.nickname = ""
        self.realname = ""

        self.nick_set = False

        self.server_mem = mem

        self.commands = [
            "CAP",
            "NICK",
            "USER",
            "QUIT",
            "JOIN",
            "PRIVMSG"
        ]

    def loop(self):
        try:
            while True:
                msg = self.socket.recv(4096)
                if msg:
                    msg = msg.decode().split('\r\n')

                    for part in msg:
                        print(part)
                        self.check_command(part)
        except ConnectionResetError:
            print("connection reset")
        except BrokenPipeError:
            print("Broken pipe")
    
    def check_command(self, cmd):
        cmd = cmd.split(" ")
        if cmd[0] in self.commands:
            if cmd[0] == "NICK":
                self.set_nickname(cmd[1])
            elif cmd[0] == "USER":
                self.set_realname(cmd[1])
            elif cmd[0] == "QUIT":
                self.server_mem.socket_list.remove(self.socket)
                del self.server_mem.clients[self.socket]
            elif cmd[0] == "JOIN":
                self.join_channel(self.socket, cmd[1])
            elif cmd[0] == "PRIVMSG":
                self.message(self.socket, cmd[1], " ".join(cmd[2:]))
    
    def set_nickname(self, nickname):
        if len(nickname) > 9 or nickname[0] == "-":
            print("Client tried to connect with invalid username")
            code = "432"
            msg = f"'{nickname}' is invalid."
            self.send_code(code, self.socket, msg, nickname)
            return False
        
        try:
            if int(nickname[0]):
                print("Client tried to connect with invalid username")
                code = "432"
                msg = f"'{nickname}' is invalid."
                self.send_code(code, self.socket, msg, nickname)
                return False
        except ValueError:
            pass
        
        for client in self.server_mem.clients:
            if self.server_mem.clients[client] == nickname:
                print("Client tried to connect with taken username")
                code = "436"
                msg = f"'{nickname}' is already taken."
                self.send_code(code, self.socket, msg, nickname)
                return False
        
        self.nickname = nickname
        
        msg = f"NICK {nickname}"
        self.send_message_from_server(self.socket, msg)
        self.server_mem.clients[self.socket] = self.nickname
    
    def set_realname(self, name):
        self.realname = name
        
        self.server_mem.clients[self.socket] = self.nickname
        self.server_mem.socket_list.append(self.socket)

        msg = f"Welcome to the Internet Relay Network {self.nickname}!{self.nickname}@{self.address}"
        self.send_code("001", self.socket, self.nickname, msg)

        msg = f"Your host is {self.server_mem.ipv4_address}, running version {self.server_mem.server_name}"
        self.send_code("002", self.socket, self.nickname, msg)

        msg = f"This server was created in 2000 - no wait, that's the protocol. The server was made 20 years after everyone stopped using IRC."
        self.send_code("003", self.socket, self.nickname, msg)

        msg = f"my-awful-irc-server v420.69"
        self.send_code("004", self.socket, self.nickname, msg)

    def join_channel(self, sckt, chan):
        if chan in self.server_mem.channels:
            self.server_mem.channels[chan].append(sckt)
            for socket in self.server_mem.channels[chan]:
                msg = f"{self.nickname}!{self.realname}@{self.address} JOIN {chan}"
                self.send_message(socket, msg)
            
            msg = f"332 {chan} :{chan} no topic"
            self.send_message_from_server(sckt, msg)

            chan_members = []
            for socket in self.server_mem.channels[chan]:
                chan_members.append(self.server_mem.clients[socket])
            chan_members = " ".join(chan_members)
            msg = f"353 {self.nickname} = {chan} :{chan_members}"
            self.send_message_from_server(sckt, msg)

            msg = f"366 {chan} :End of NAMES list"
            self.send_message_from_server(sckt, msg)

    def message(self, sckt, chan, msg):
        if chan[0] == "#":
            for client in self.server_mem.channels[chan]:
                if client != self.socket:
                    self.send_message_from_user(client, msg, chan)
        else:
            found = False
            for client in self.server_mem.clients:
                if self.server_mem.clients[client] == chan:
                    self.send_message_from_user(client, msg, chan)
                    found = True

    def send_code(self, code, sckt, usr, msg):
        sckt.send(f":{self.server_mem.ipv4_address} {code} {usr} {msg}\r\n".encode())
        print(f":{self.server_mem.ipv4_address} {code} {usr} {msg}\r\n")
    
    def send_message_from_server(self, sckt, msg):
        sckt.send(f":{self.server_mem.ipv4_address} {msg}\r\n".encode())
        print(f":{self.server_mem.ipv4_address} {msg}\r\n")
    
    def send_message_from_user(self, sckt, msg, chan):
        sckt.send(f":{self.nickname}!{self.realname}@{self.address} PRIVMSG {chan} {msg}\r\n".encode())
        print(f"from {self.nickname} to {chan}:{self.nickname}!{self.realname}@{self.address} PRIVMSG {chan} {msg}")

    def send_message(self, sckt, msg):
        sckt.send(f":{msg}\r\n".encode())
        print(f":{msg}\r\n")