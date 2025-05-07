
import time
from protocol import *
import sys
import pyaudio
from functools import partial
import threading
from PyQt5.QtCore import QTimer
import ast
# Constants
BUFFER_SIZE: int = 1024

CHUNK = 1024
FORM = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 3

# Class Client_BL
class Client_BL:

    # Init function
    def __init__(self, ip, port):
        self.ip = ip

        self.msg_callback = None
        self.voting_callback = None
        self.vote_callback = None

        self.timer_callback = None
        self.DYM_callback = None

        self.flag = 0
        self.port = int(port)
        self.socket = None
        self.receive_image_flag = None
        self.start_stream_callback = None
        self.audio_stream_active = False
        self.audio_stream_thread = None
        self.add_song_into_voting_callback = None
        self.del_button_callback = None

        self.p = None
        self.stream = None



    def connect(self):

        # Save the start time of the function,
        start_time = time.time()
        timeout = 0.5

        """ if after the time has elapsed we are unable to connect to the server,
        program will return an error """

        while time.time() - start_time < timeout:
            try:
                # Create and connect socket
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.ip, self.port))

                # Add data into log file
                write_to_log(f"[CLIENT]{self.socket.getsockname()} connected")

                # Return client socket object
                return self.socket
            except Exception as e:
                # Handle failure
                write_to_log(f"[CLIENT] failed to connect client; error:{e}")
                return None

    def send(self, msg):
        try:
            msg = msg.encode(FORMAT)
            self.socket.sendall(len(msg).to_bytes(4, byteorder='big'))
            # Send message
            self.socket.sendall(msg)

            write_to_log(f"[CLIENT_BL] send {self.socket.getsockname()} {msg} ")
            return True
        except Exception as e:
            write_to_log(f"[CLIENT_BL] failed to send_data; error: {e}")
            return False

    def add_callbacks(self, msg_func, voting_func, vote_func, timer_func, DYM_func, add_song_func, del_button, stream_callback):
        self.msg_callback = msg_func
        self.voting_callback = voting_func
        self.vote_callback = vote_func
        self.timer_callback = timer_func
        self.DYM_callback = DYM_func
        self.add_song_into_voting_callback = add_song_func
        self.del_button_callback = del_button
        self.start_stream_callback = stream_callback

    def countdown(self, sec):
        while sec != 0:
            time.sleep(1)
            sec -= 1
            QTimer.singleShot(0, partial(self.timer_callback))

    def leave_the_room(self):
        self.audio_socket.close()

    def receive(self):
        while True:

                msg_len_data = self.socket.recv(4)
                if not msg_len_data:
                    break


                msg_len = int.from_bytes(msg_len_data, byteorder='big')

                msg = self.socket.recv(msg_len).decode('utf-8')

                if not msg:
                    break
                try:
                    print(f"received {msg}")
                except:
                    pass
                msg = msg.split(" ")
                cmd = msg.pop(0)
                print("COMMAND: " + cmd)
                write_to_log(f"[CLIENT_BL] receive {self.socket.getsockname()} {msg}")

                if cmd == "MSG":
                    login = msg.pop(0)
                    msg = " ".join(msg)
                    msg = [[login, msg]]
                    QTimer.singleShot(0, partial(self.msg_callback, msg))
                if cmd == "MSGS":
                    msg = " ".join(msg)
                    msg_list = ast.literal_eval(msg)
                    QTimer.singleShot(0, partial(self.msg_callback, msg_list))

                if cmd == "VOTING":
                    timer = int(msg.pop(0))
                    room = msg.pop(0)
                    msg = " ".join(msg)
                    try:
                        songs = ast.literal_eval(msg)
                        for song in songs:
                            print(song.split("::::")[0])
                        QTimer.singleShot(0, partial(self.voting_callback, songs, timer))
                    except:
                        pass
                if cmd == "VOTE":
                    song = " ".join(msg)
                    QTimer.singleShot(0, partial(self.vote_callback, song, 0, 1))
                if cmd == "PORT":
                    port = msg[0]
                    try:
                        # Create and connect socket
                        self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.audio_socket.connect((self.ip, int(port)))

                        msg_len_data = self.audio_socket.recv(4)
                        if not msg_len_data:
                            break

                        msg_len = int.from_bytes(msg_len_data, byteorder='big')
                        msg = self.audio_socket.recv(msg_len).decode(FORMAT)
                        msg = msg.split(" ")
                        cm = msg.pop(0)
                        if cm == 'STREAM':
                            cmd ="STREAM"

                    except:
                        print("something went wrong")

                if cmd == "STREAM":
                    link = msg.pop(-1)
                    song = " ".join(msg)

                    QTimer.singleShot(0, partial(self.start_stream_callback, song, link))
                    p = pyaudio.PyAudio()
                    stream = p.open(format=FORM,
                                    channels=CHANNELS,
                                    rate=RATE,
                                    output=True,
                                    frames_per_buffer=CHUNK)
                    thread = threading.Thread(target=self.receive_stream, args=(stream,))
                    thread.start()
                if cmd == "DYM":
                    songs = " ".join(msg)
                    songs = songs.split("///")
                    songs.pop(-1)
                    QTimer.singleShot(0, partial(self.DYM_callback, songs))

                if cmd == "ADD_SONG":
                    song = " ".join(msg)
                    QTimer.singleShot(0, partial(self.add_song_into_voting_callback, song))

                if cmd == "DEL_BUTTON":
                    QTimer.singleShot(0, partial(self.del_button_callback))

    def receive_stream(self, stream):
        while True:
            try:
                self.audio_socket.settimeout(1)
                data = self.audio_socket.recv(CHUNK)
                if not data:
                   break
                stream.write(data)
            except:
                break



