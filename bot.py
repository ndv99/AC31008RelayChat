import socket
import random
import sys
import string
import client

class Bot(client.Client):

    def __init__(self):
        pass

    def listen(self):
        pass

    def check_for_command(self):
        pass

    def reply(self):
        pass

    def parse_server_data(self):
        pass
    
    def bot_test_method(self):
        print("This is a test from the 'Bot' class.")

print("This is the bot file.")

bot = Bot()
bot.client_test_method()
bot.bot_test_method()