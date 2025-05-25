from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes


from cryptography.fernet import Fernet



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
        super().__init__()

        self.ip = ip

        self.flag = 0
        self.port = int(port)


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


                # receive encryption key
                msg_len_data = self.socket.recv(4)
                if not msg_len_data:
                    break
                msg_len = int.from_bytes(msg_len_data, byteorder='big')

                self.servers_public_key = self.socket.recv(msg_len).decode('utf-8')

                # Generate private key
                self.private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                )
                # Get public key from private key
                self.public_key = self.private_key.public_key()

                # Return client socket object
                return self.socket
            except Exception as e:
                # Handle failure
                write_to_log(f"[CLIENT] failed to connect client; error:{e}")
                return None
    def get_public_key(self):
        key = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        return key

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

    def add_callbacks(self, msg_func, voting_func, vote_func, timer_func, DYM_func, add_song_func, del_button,
                      stream_callback, new_usr, skip_poll, update_barchart, skip_song, clear_song_info):
        self.msg_callback = msg_func
        self.voting_callback = voting_func
        self.vote_callback = vote_func
        self.timer_callback = timer_func
        self.DYM_callback = DYM_func
        self.add_song_into_voting_callback = add_song_func
        self.del_button_callback = del_button
        self.start_stream_callback = stream_callback
        self.new_usr = new_usr
        self.skip_poll = skip_poll
        self.update_barchart = update_barchart
        self.skip_song = skip_song
        self.clear_song_info = clear_song_info

    def countdown(self, sec):
        while sec != 0:
            time.sleep(1)
            sec -= 1
            QTimer.singleShot(0, partial(self.timer_callback))

    def leave_the_room(self):
        self.audio_socket.close()

    def set_login(self, login):
        pass

    # Listening to server
    def receive(self):
        while True:
            # Receive message logic
            msg_len_data = self.socket.recv(4)
            if not msg_len_data:
                break
            msg_len = int.from_bytes(msg_len_data, byteorder='big')
            msg = self.socket.recv(msg_len).decode('utf-8')

            if not msg:
                break

            msg = msg.split(" ")
            cmd = msg.pop(0)
            write_to_log(f"[CLIENT_BL] receive {self.socket.getsockname()} {msg}")

            # Message in chat
            if cmd == "MSG":
                login = msg.pop(0)
                msg = " ".join(msg)
                msg = self.decrypt_message(msg)
                msg = [[login, msg]]
                QTimer.singleShot(0, partial(self.msg_callback, msg))
            # List of messages
            if cmd == "MSGS":
                # Amount of users in the room
                numOfUsers = msg.pop(0)
                # join message to list looking string
                msg = " ".join(msg)
                msg_list = ast.literal_eval(msg)

                decrypted_list = []
                # loop for decrypting every message
                for login, enc_msg, time in msg_list:
                    decrypted_msg = self.decrypt_message(enc_msg)
                    decrypted_list.append([login, decrypted_msg])
                # display messages in chat
                QTimer.singleShot(0, partial(self.msg_callback, decrypted_list))
                # Updates skip poll if it exists
                QTimer.singleShot(0, partial(self.new_usr, numOfUsers))

            # new poll
            if cmd == "POLL":
                # timer
                timer = int(msg.pop(0))
                room = msg.pop(0)
                msg = " ".join(msg)
                try:
                    # converting string into dict
                    songs = ast.literal_eval(msg)
                    # display poll
                    QTimer.singleShot(0, partial(self.voting_callback, songs, timer))
                except:
                    pass
            # someone voted in poll (we need this to update polls)
            if cmd == "VOTE":
                song = " ".join(msg)
                QTimer.singleShot(0, partial(self.vote_callback, song, 0, 1))
            # port for audio streaming
            if cmd == "PORT":
                port = msg[0]
                try:
                    # Create and connect socket
                    self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.audio_socket.connect((self.ip, int(port)))

                    # Receive cmd
                    msg_len_data = self.audio_socket.recv(4)
                    if not msg_len_data:
                        break
                    msg_len = int.from_bytes(msg_len_data, byteorder='big')
                    msg = self.audio_socket.recv(msg_len).decode(FORMAT)

                    msg = msg.split(" ")
                    cm = msg.pop(0)
                    if cm == 'START_STREAM':
                        cmd ="START_STREAM"

                except:
                    pass
            # stream started -> display song's info and start receiving stream
            if cmd == "START_STREAM":

                msg = " ".join(msg)

                # song`s data
                link = msg.split(":::").pop(-1)
                song = msg.split(":::").pop(1)
                artist = msg.split(":::").pop(0)

                QTimer.singleShot(0, partial(self.start_stream_callback, artist, song, link))
                # pyaudio setting
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
            if cmd == "NEW_USER":
                QTimer.singleShot(0, partial(self.new_usr, 1))
            if cmd == "USER_LEFT":
                QTimer.singleShot(0, partial(self.new_usr, -1))
            if cmd == "SKIP_POLL":
                QTimer.singleShot(0, partial(self.skip_poll))
            if cmd == "UPDATE_BARCHART":
                QTimer.singleShot(0, partial(self.update_barchart, int(msg[0]), int(msg[1])))
            if cmd == "SKIP_SONG":
                QTimer.singleShot(0, partial(self.skip_song))
            if cmd == "KEY":
                # 1. Join the received encrypted key parts
                key = " ".join(msg)

                # 2. Decode the Base64 string into bytes
                encrypted_key_bytes = base64.b64decode(key)

                # 3. Use the private key to decrypt (no need to load it again)
                self.key = self.private_key.decrypt(
                    encrypted_key_bytes,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )

                # 4. Convert to string if needed
                key_str = self.key.decode()
                self.fernet = Fernet(self.key)

    def encrypt_with_public_key(self, message):
        # 1. Convert public key string (PEM) to object
        public_key = serialization.load_pem_public_key(self.servers_public_key.encode())

        # 2. Encrypt the message using the public key
        encrypted = public_key.encrypt(
            message.encode(),  # Convert message to bytes
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # 3. Return base64-encoded string (safe for transport)
        return base64.b64encode(encrypted).decode()



    def encrypt_message(self, message):
        encrypted = self.fernet.encrypt(message.encode())  # convert to bytes before encryption
        return encrypted.decode()

    def decrypt_message(self, encrypted_message):
        decrypted_bytes = self.fernet.decrypt(encrypted_message.encode())
        return decrypted_bytes.decode()


    # loop for receiving audio stream
    def receive_stream(self, stream):
            while True:
                try:
                    self.audio_socket.settimeout(1)
                    data = self.audio_socket.recv(CHUNK)
                    if not data:
                        QTimer.singleShot(0, partial(self.clear_song_info))
                        break
                    stream.write(data)
                except:
                    QTimer.singleShot(0, partial(self.clear_song_info))
                    break



