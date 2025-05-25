import time
from http.client import responses

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

import bcrypt
import base64



import pyaudio
import wave
from db import *
from song_url import *
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from Session import *
from Active_votings import *
import av

# -*- coding: utf-8 -*-from pydub import AudioSegment

import random
import os
from pathlib import Path
import subprocess
# Constants

# Server accept all income connections
SRV_IP = "0.0.0.0"

# Constants for wav audio reading library
BUFFER_SIZE: int = 1024
CHUNK_SIZE = 1024
# Size of each chunk (4 KB)
FORM = pyaudio.paInt16
CHANNELS = 2
RATE = 44100


output_path = Path("songs")


# Class Server_BL
class Server_BL():
    # Init function
    def __init__(self, port, client_callback, message_callback):

        self.port = port
        self.ping_port = 12345

        # Dictionary where keys are the name of the rooms and the value is list which contains two numbers,
        # first id amount of people voted for skip and the second is total amount of people in room
        # Lists for users in session and current polls
        self.session = []
        self.votings = []


        self.ping_sockets = {}

        # Generate a new private RSA key
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,  # Commonly used public exponent
            key_size=2048  # Key size in bits (use 3072 or 4096 for more security)
        )

        # Derive the public key from the private key
        public_key = self.private_key.public_key()
        # Serialize the private key to PEM format (as bytes)
        self.public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        # Dict which saves audio sockets of users of each room
        self.roomsNusers = {}


        # Callback which adds new client into the table
        self.client_callback = client_callback
        # Callback which displays logg data
        self.message_callback = message_callback
        self.server = None
        self.SRV_RUNNING = None

    # Func that sets boolean variable whether server running or not
    def set_server_running_flag(self, flag):
        self.SRV_RUNNING = flag

    # Start server func
    def start_server(self):
        try:
            self.set_server_running_flag(True)
            SRV_ADDR = (SRV_IP, self.port)
            write_to_log("[SERVER] starting")
            # Create and connect socket
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(SRV_ADDR)
            self.server.listen()
            write_to_log(f"[SERVER] listening on {SRV_IP}")

            while self.SRV_RUNNING:
                # Save connected client data
                client_socket, addr = self.server.accept()
                # If new client connected , running separate thread to handle him
                if client_socket:
                    # Sending server`s public key

                    self.send_message(client_socket, f"PUBLIC_KEY {self.public_key}")

                    # Create a separate thread for each new client
                    self.client_callback(addr)
                    thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                    thread.start()
                    write_to_log(f"[SERVER] ACTIVE CONNECTION {threading.active_count() - 2}")

        except Exception as e:
            # Handle failure
            write_to_log(f"[Server] failed to set up server {e}")



    # Client handle function, will receive everything from client, and send back
    def handle_client(self, client_socket, addr):
        db = database()
        # This code run in separate for every client
        write_to_log(f"[SERVER] NEW CONNECTION: {addr} connected")
        connected = True
        log = ''
        try:
            while connected:

                # Get message size
                msg_size = int.from_bytes(client_socket.recv(4), byteorder='big')
                # Get message from  client

                msg = client_socket.recv(msg_size).decode(FORMAT)

                if not msg:
                    print(f"Client has disconnected")
                    break
                self.message_callback(msg)
                message = msg.split(" ")
                cmd = message.pop(0)

                write_to_log(f"[SERVER] received message from {addr} - {msg}")


                if(cmd == "REG"):
                    self.sign_up_function(db, message, client_socket)
                elif cmd == "LOG":
                    log = self.login_func(db, message, client_socket, addr)
                elif cmd == "CON":
                    self.connect_to_the_room(message, db, client_socket)
                elif cmd == "LEV":
                    self.leave_the_room(message, db, client_socket)
                elif cmd == "MSG":
                    self.handle_message(message, db)
                elif cmd == "VOTE":
                    self.handle_vote(message)
                elif cmd == "FIND_SONG":
                    self.find_song(message, client_socket)
                elif cmd == "ADD_SONG":
                    self.add_song(message)
                elif cmd == "SKIP":
                    self.skip_func(message[0], db)
                elif cmd == "GUEST":
                    log = self.guest_func(message, db, client_socket, addr)
                elif cmd == "BYE":
                    self.disconnect_client(db, log)
        except:
            self.disconnect_client(db, log)

    def disconnect_client(self, db, log):
        for user in self.session:
            if user.get_log() == log:
                self.session.remove(user)
                user.get_soc().close()
        db.set_isLogged(log, False)

    def guest_func(self, message, db, client_socket, addr):
        nickname = message[0]
        if (db.if_user_in_db(nickname) == False):
            # Add new user
            db.new_user(nickname, nickname, 'Guest')
            self.session.append(Session(addr[0], addr[1], client_socket, message[0]))
            # Send message size
            response = "0"

            db.set_isLogged(nickname, True)
            res = nickname

        else:
            response = "1"
            res = None


        client_socket.sendall(len(response).to_bytes(4, byteorder='big'))
        # Send message
        client_socket.sendall(response.encode())
        return res

    def skip_func(self, room, db):
        skip_list = db.get_skipPollList(room)
        skip_list[0] = skip_list[0] + 1
        skip_list[1] = self.count_users(room)
        db.set_skipPollList(room, skip_list)
        self.update_barchart(room, db)


    # SIGH UP AND LOGIN FUNCTIONS
    def sign_up_function(self, db, message, client_socket):
        login = message.pop(0)
        encrypted_password = " ".join(message)

        if (db.if_user_in_db(login) == False):
            password = self.decrypt_password(encrypted_password)

            # hash password with salt
            hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            # Add new user
            db.new_user(login, hash_password, 'User')
            # Send message size
            response = "Successfully registered"

        else:
            # Send message size
            response = "Username already taken"

        client_socket.sendall(len(response).to_bytes(4, byteorder='big'))
        # Send message
        client_socket.sendall(response.encode())

    def login_func(self, db, message, client_socket, addr):
        # Extract login from list
        login = message.pop(0)
        # Joining everything else together -> encrypted password
        encrypted_password = " ".join(message)
        # Decrypting password
        entered_password = self.decrypt_password(encrypted_password)
        # Get password's hash from database
        password = db.get_user_password(login)
        log = ''
        # If there is no such user
        if password == None:
            password_matches = False
        else:
            # Else we compare hash from database with entered password (password_matches - boolean)
            password_matches = bcrypt.checkpw(entered_password.encode(), password)
        if password_matches == True:
            # response which we send to the client
            response = 'true'
            # Add user to list which contains all currently connected users
            self.session.append(Session(addr[0], addr[1], client_socket, login))
            # Indicates in the database that the user is now online (logged in)
            db.set_isLogged(login, True)
            log = login
        else:
            # response
            response = 'false'
            # user's login
            log = ''

        # Send message size
        client_socket.sendall(len(response).to_bytes(4, byteorder='big'))
        # Send message
        client_socket.sendall(response.encode(FORMAT))
        # return user's login
        return log

    def decrypt_password(self, encrypted_password):

        # decode to bytes
        encrypted_bytes = base64.b64decode(encrypted_password)

        # decrypt
        password = self.private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode()


        return password



    # Function to hash a password
    def hash_password(self, plain_password) -> bytes:
        # Convert string to bytes
        password_bytes = plain_password.encode('utf-8')

        # Generate salt
        salt = bcrypt.gensalt()  # You can specify complexity: bcrypt.gensalt(rounds=12)

        # Hash password with salt
        hashed = bcrypt.hashpw(password_bytes, salt)

        return hashed

    # users_public is expected to be a PEM-encoded public key string
    def encrypt_symmetric_key_with_public_key(self, users_public: str, symmetric_key: bytes) -> bytes:
        # Load public key
        public_key = serialization.load_pem_public_key(users_public.encode())

        # Encrypt symmetric key
        encrypted_key = public_key.encrypt(
            symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_key  # Still in bytes form

    def connect_to_the_room(self, message, db, client_socket):

        # Get username
        room = message.pop(0)
        user = message.pop(0)
        users_public = " ".join(message)


        # If that client is the first one connected to this room
        if not room in self.roomsNusers:
            # Dictionary with room names as a jey, and list with connected sockets as a value
            self.roomsNusers[room] = []

            port = self.add_port(room, db)


            db.new_room(room, port, self.count_users(room))

            thread = threading.Thread(target=self.create_audio_socket, args=(room, port, ))
            thread.start()



        # Get symmetric key of the room
        key = db.get_key(room)

        #Converting string into bytes
        key_bytes = key.encode()

        encrypted_key = self.encrypt_symmetric_key_with_public_key(users_public, key_bytes)

        encrypted_key_str = base64.b64encode(encrypted_key).decode()

        self.send_message(client_socket, f"KEY {encrypted_key_str}")

        self.send_message_to_everybody(room, "NEW_USER")

        # Sending previous messages in chat to connected user (also poll if he is the first user in room)
        for usr in self.session:
            if (usr.get_log() == user):
                usr.set_room(room)
                messages = f'MSGS {self.count_users(room)} {str(db.get_messages(room))}'

                self.send_message(client_socket, messages)

                count = self.count_users(room)
                # If that is the first user in the room, server send the first voting to the client
                if count == 1:
                    for voting in self.votings:
                        if voting.get_room() == room:
                            self.votings.remove(voting)
                    self.send_songs_for_vote(room, 0)

        # If there is already poll in the room -> send it to user
        for voting in self.votings:
            if voting.get_room() == room and voting.get_status() == False:
                message = f"VOTING {str(voting.get_timer())} {room} {str(voting.get_songs())}"

                self.send_message(client_socket, message)

                for song, votes in voting.get_songs().items():
                    for i in range(votes):
                        msg = f"VOTE {song}"

                        self.send_message(client_socket, message)


        msg = f"PORT {db.get_port(room)}"
        self.send_message(client_socket, msg)

        if db.get_isSkipPollActive(room) == 1:
            message = f"SKIP_POLL"
            self.send_message(client_socket, message)

        skip_poll_list = db.get_skipPollList(room)
        skip_poll_list[1] = self.count_users(room)
        db.set_skipPollList(room, skip_poll_list)
        self.update_barchart(room, db)



    # GENERAL OPTIMISATION FUNCTIONS

    def send_message_to_all_users(self, room, msg):
        for usr in self.session:
            if (usr.get_room() == room):
                # Send message size
                sock = usr.get_sock()

                sock.sendall(len(msg.encode(FORMAT)).to_bytes(4, byteorder='big'))
                # Send message
                sock.sendall(msg.encode(FORMAT))

    def send_for_everyone_except_sender(self, room, login, msg):
        for usr in self.session:
            if (usr.get_room() == room and usr.get_log() != login):
                # Send message size
                sock = usr.get_sock()

                sock.sendall(len(msg.encode(FORMAT)).to_bytes(4, byteorder='big'))
                # Send message
                sock.sendall(msg.encode(FORMAT))

    def send_message(self, client_socket, message):
        client_socket.sendall(len(message.encode(FORMAT)).to_bytes(4, byteorder='big'))
        # Send message
        client_socket.sendall(message.encode(FORMAT))


    # FUNCTIONS CONCERN POLLS

    # Add song into the poll
    def add_song(self, message):
        room = message.pop(0)
        # Loop where we find the current voting among all polls in our list
        for voting in self.votings:
            if voting.get_room() == room:
                # Check if there is less than 10 songs in poll
                if voting.count_songs() <= 10:
                    song = " ".join(message)
                    voting.add_song(song)
                    # Notify users that new song was added into the poll
                    msg = f"ADD_SONG {song}"
                    self.send_message_to_all_users(room, msg)
                if voting.count_songs() >= 10:
                    msg = f"DEL_BUTTON"
                    self.send_message_to_all_users(room, msg)

    # Func which return to user search results
    def find_song(self, song, client_socket):
        song = " ".join(song)
        # Function which receives user`s input and return top 3 spotify results by that request
        songs_list = search_songs(song)

        messages = f'DYM {str(songs_list)}'
        # Sending search results to that user
        client_socket.sendall(len(messages.encode(FORMAT)).to_bytes(4, byteorder='big'))
        # Send message
        client_socket.sendall(messages.encode(FORMAT))

    #  Func which activates when someone elect song
    def handle_vote(self, message):
        room = message.pop(0)
        # login of voted user
        login = message.pop(0)
        song = " ".join(message)
        msg = f"VOTE {song}"
        self.send_for_everyone_except_sender(room, login, msg)

        # Loop for finding poll in polls list
        for voting in self.votings:
            if voting.get_room() == room:
                # Adding vote into current voting dictionary
                voting.add_vote(song)
                # If it is the first vote, then the 30 seconds timer starts.1
                if (sum(voting.get_songs().values()) == 1):
                    # If it is the first vote, start countdown
                    thread = threading.Thread(target=self.start_timer(voting), args=())
                    thread.start()

    # When someone send message in chat
    def handle_message(self, message, db):
        # Pop values from command list
        room = message.pop(0)
        login = message.pop(0)
        # Join the list to string
        message = " ".join(message)
        # Saving message into database
        db.add_message(room, login, message)
        msg = "MSG " + login + " " + message
        # From all users connected to server
        self.send_message_to_all_users(room, msg)

    # When client leave the room, func deletes him from the list
    def leave_the_room(self, message, db, client_socket):
        # user`s login
        room = message.pop(0)
        user = message.pop(0)

        if_voted = message.pop(0)
        # Deleting user from room


        self.send_message_to_all_users(room, "USER_LEFT")



        # Searching that exact user among the session list
        for usr in self.session:
            if (usr.get_log() == user):
                # Setting room variable for the user None
                usr.set_room(None)
            # Counting people in room
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if self.count_users(room) == 0:
            # If there is no users currently in the room, delete the voting
            for voting in self.votings:
                if voting.get_room() == room:
                    self.votings.remove(voting)
            db.set_isSkipPollActive(room, False)
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
        skip_list = db.get_skipPollList(room)
        skip_list[1] = self.count_users(room)
        if int(if_voted) == 1:
            skip_list[0] -= 1
        db.set_skipPollList(room, skip_list)
        self.update_barchart(room, db)


    def update_barchart(self, room, db):

        if (db.get_isSkipPollActive(room) == 1) and (db.get_skipPollList(room)[1] !=0) :
            if int(db.get_skipPollList(room)[0])/int(db.get_skipPollList(room)[1]) > 0.5:
                self.send_message_to_everybody(room, "SKIP_SONG")
                for voting in self.votings:
                    if voting.get_room() == room:
                        self.votings.remove(voting)
                db.set_isSkipPollActive(room, False)
                skip_list = db.get_skipPollList(room)
                skip_list[0] = 0
                skip_list[1] = self.count_users(room)
                db.set_skipPollList(room, skip_list)
                # Send new voting
                self.send_songs_for_vote(room, 0)
            else:
                skip_list = db.get_skipPollList(room)
                self.send_message_to_everybody(room, f"UPDATE_BARCHART {skip_list[0]} {skip_list[1]}")

    # Generating port for streaming music
    def add_port(self, room, db):
        port = random.randint(1024, 65535)
        if port not in db.get_all_ports() and port != self.port:
            return port
        else: return self.add_port(room, db)


    # Creating audio socket for specific room
    def create_audio_socket(self, room, port):
        audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        audio_socket.bind(("", port))
        audio_socket.listen(5)
        db = database()
        while True:
            user_audio, addr = audio_socket.accept()
            # If there is no currently stream
            if db.get_isStreaming(room) == 0:
                msg = 'FINE'
            # Else we are sending all the data about current song.
            else:
                info = db.get_currentSong(room)
                msg = f"START_STREAM {info}"

            self.send_message(user_audio, msg)
            if room not in self.roomsNusers:
                self.roomsNusers[room] = []
            self.roomsNusers[room].append(user_audio)

    # When we download song from youtube it downloads in webm format,
    # however streaming wav format file is much better
    def convert_webm_to_wav(self, input_file, output_file):

        container = av.open(input_file)
        audio_stream = container.streams.audio[0]
        output = av.open(output_file, 'w')
        output_stream = output.add_stream('pcm_s16le', rate=audio_stream.rate, channels=audio_stream.channels)

        for frame in container.decode(audio_stream):
            output_stream.encode(frame)
        output.close()

    def streaming_current_file(self, room, db):
        # Ensure the directory exists and is not empty
        folder_path = Path("songs") / room
        if folder_path.exists() and len(os.listdir(folder_path)) > 0:
            files = list(folder_path.iterdir())
            song = files[0].name  # Assuming the first file is the one we want
            if os.path.exists(f"songs/{room}") and os.listdir(f"songs/{room}"):

                folder_path = Path("songs") / room
                files = list(folder_path.iterdir())

                song = files[0].name

                wf = wave.open(f'songs/{room}/{song}', 'rb')
                song = db.get_currentSong(room)
                self.send_message_to_everybody(room, f"START_STREAM {song}")
                db.set_isStreaming(room, True)

                # Audio file parameters
                framerate = wf.getframerate()
                sample_width = wf.getsampwidth()
                num_channels = wf.getnchannels()
                bytes_per_frame = sample_width * num_channels

                # Frames in 30 seconds
                frames_30_sec = framerate * 5

                frames_sent = 0

                skip_triggered = False
                while True:
                    if db.get_isDownloading(room) == False:
                        data = wf.readframes(CHUNK_SIZE)
                        if not data:
                            self.get_recommendations(song, [], self.session, room)
                            break

                        count = 0
                        for audio_socket in self.roomsNusers[room]:
                            try:
                                count += 1
                                audio_socket.sendall(data)


                            except:
                                try:
                                    self.roomsNusers[room].remove(audio_socket)
                                    audio_socket.close()
                                except ValueError:
                                    pass
                        if count == 0:
                            db.set_isStreaming(room, False)
                            return

                        #Frames count
                        frames_sent += len(data) // bytes_per_frame

                        # Here we catch the moment when song on 30 seconds
                        if frames_sent >= frames_30_sec and skip_triggered == False:
                            self.send_message_to_everybody(room, "SKIP_POLL")
                            db.set_isSkipPollActive(room, True)
                            skip_triggered = True
                    else:
                        break


    def encrypt_msg(self, room, message):
        db = database()
        key = db.get_key(room)
        fernet = Fernet(key.encode())  # Ensure key is in bytes
        encrypted_bytes = fernet.encrypt(message.encode())  # Encrypt message
        return encrypted_bytes.decode()

    def download_and_stream_song(self, song_name, artist_name, link, room):
        db = database()
        db.set_currentSong(room, f"{artist_name}:::{song_name}:::{link}")
        db.set_isDownloading(room, True)
        db.set_isStreaming(room, False)

        time.sleep(0.5)
        msg = self.encrypt_msg(room, "Downloading the song...")
        msg = f"MSG Dj_Arbuzz {msg}"

        self.send_message_to_all_users(room, msg)

        # Deleting songs if they are any
        folder_path = Path("songs") / room
        if folder_path.exists():
            [file.unlink() for file in folder_path.glob("*") if file.is_file()]

        # Downloading the song

        output_dir = f"songs/{room}"
        os.makedirs(output_dir, exist_ok=True)

        # Construct the yt-dlp command
        # Construct the yt-dlp command
        command = [
            "yt-dlp",
            f"ytsearch1: {song_name} - {artist_name} official audio",  # Search for the song by name
            "-x",  # Extract audio
            "--audio-format", "wav",  # Convert to WAV format
            "-o", f"{output_dir}/%(title)s.%(ext)s",  # Save in the specified directory
            "--match-filter", "duration < 600",  # Filter out long videos (e.g., >10 minutes)
            "--ffmpeg-location", "C:/Users/SaLu/Groove bros/ffmpeg/bin"
        ]

        # Run the command
        result = subprocess.run(command, capture_output=True, text=True)


        db.set_isDownloading(room, False)
        # if the room is empty, deleting downloaded song
        if self.count_users(room) == 0:
            folder_path = Path("songs") / room
            if folder_path.exists():
                [file.unlink() for file in folder_path.glob("*") if file.is_file()]
            return

        self.streaming_current_file(room, db)

    def start_timer(self, voting):
        db = database()
        chosen_song = voting.start_timer()


        art = chosen_song.split("::::")
        song_name = art.pop(0)
        art = "::::".join(art)
        song_artist = art.split(":::::")[0]
        link = art.split(":::::")[-1]


        msg = f"The next song is: {song_name} \n {song_artist}"
        for usr in self.session:
            if (usr.get_room() == voting.get_room()):
                # Send message size
                sock = usr.get_sock()
                sock.sendall(len(msg).to_bytes(4, byteorder='big'))
                # Send message
                sock.sendall(msg.encode())


        thread = threading.Thread(target=self.download_and_stream_song, args=(song_name, song_artist, link , voting.get_room()))
        thread.start()

    def send_message_to_everybody(self, room, message):
        for usr in self.session:
            if (usr.get_room() == room):
                # Send message size
                sock = usr.get_sock()
                sock.sendall(len(message).to_bytes(4, byteorder='big'))
                # Send message
                sock.sendall(message.encode())





    def count_users(self, room):
        count = 0
        for usr in self.session:
            if (usr.get_room() == room): count += 1
        return count


    def send_songs_for_vote(self, room, song):
        thread = threading.Thread(target=self.get_recommendations, args=(song, [], self.session, room))
        thread.start()

    def get_recommendations(self, song, recent_songs, session, room):

        response_text = get_songs_by_genre(room)
        message = f"POLL 4 {room} {response_text}"

        for voting in self.votings:
            if voting.get_room() == room:
                self.votings.remove(voting)

        self.votings.append(Voting(room, response_text))
        for usr in session:
            if (usr.get_room() == room):
                # Send message size
                sock = usr.get_sock()
                sock.sendall(len(message).to_bytes(4, byteorder='big'))
                # Send message
                sock.sendall(message.encode())

    # Quit server function
    def quit_server(self):
        self.server.close()
        #write_to_log("[SERVER] server is disabled")
