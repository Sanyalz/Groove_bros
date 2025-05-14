import socket
import time
from protocol import *

import threading
# Constants
BUFFER_SIZE: int = 1024

# Class Client_BL
class Session:

    # Init function
    def __init__(self, ip, port, sock, login):
        self.ip = ip
        self.port = port
        self.sock = sock
        self.log = login
        self.second_sock = None
        self.room = None

    def set_log(self, login):
        self.log = login

    def set_second_sock(self, sock):
        self.second_sock = sock

    def get_second_sock(self):
        return self.second_sock

    def get_log(self):
        return self.log

    def get_sock(self):
        return self.sock

    def set_room(self, room):
        self.room = room

    def get_room(self):
        return self.room
