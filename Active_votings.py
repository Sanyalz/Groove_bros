import socket
import time
from protocol import *

import threading
# Constants
from song_class import *
BUFFER_SIZE: int = 1024

# Class Client_BL
class Voting:

    # Init function
    def __init__(self, room, songs):
        self.room = room
        self.songs = songs
        self.timer = 4
        # boolean variable which indicate if the poll finished already
        self.finished = False

    def get_room(self):
        return self.room

    def add_song(self, song):
        self.songs[song] = 0

    def count_songs(self):
        return len(self.songs)

    def get_songs(self):
        return self.songs

    def set_timer(self, timer):
        self.timer = timer

    def get_timer(self):
        return self.timer
    def get_choosen_song(self):
        return max(self.songs, key=self.songs.get)

    def add_vote(self, song):
        self.songs[song] += 1
    def start_timer(self):
        while self.timer != 0:
            time.sleep(1)
            self.timer -= 1
        self.finished = True
        return max(self.songs, key=self.songs.get)

    def get_status(self):
        return self.finished

