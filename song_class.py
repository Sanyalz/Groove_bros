import socket
import time
from protocol import *

import threading
# Constants
BUFFER_SIZE: int = 1024

# Class Client_BL
class Song:

    # Init function
    def __init__(self, name, artist, album_cover):
        self.name = name
        self.artist = artist
        self.cover = album_cover

    def get_name(self):
        return self.name

    def get_cover(self):
        return self.cover()

    def ToString(self):
        return f"{self.name}::::{self.artist}:::::{str(self.cover)}"


