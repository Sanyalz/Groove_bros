import pyaudio
import wave
from db import *
from song_url import *
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

        # Dictionary where keys are the name of the rooms and the value is list which contains two numbers,
        # first id amount of people voted for skip and the second is total amount of people in room
        self.skip_dict = {}
        # Lists for users in session and current polls
        self.session = []
        self.votings = []
        # Dict with ports of rooms (every room has its music streaming socket)
        self.ports = {}

        # Dict which store room names and number 0 or 1 as a value,
        # 1 if any song currently streamed in that room, else 0
        self.Isstreaming = {}

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
            # Loop running while the server is running
            while self.SRV_RUNNING:
                # Save connected client data
                client_socket, addr = self.server.accept()
                # If new client connected , running separate thread to handle him
                if client_socket:
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
                    log = self.login_function(db, message, client_socket, addr)
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
                    self.skip_func(message[0])
        except:
            connected = False
            for user in self.session:
                if user.get_log() == log:
                    self.session.remove(user)




    # SIGH UP AND LOGIN FUNCTIONS
    def sign_up_function(self, db, message, client_socket):
        if (db.if_user_in_db(message[0]) == False):
            # Add new user
            db.new_user(str(client_socket), message[0], message[1])
            # Send message size
            response = "Successfully registered"

            client_socket.sendall(len(response).to_bytes(4, byteorder='big'))
            # Send message
            client_socket.sendall(response.encode())
        else:
            # Send message size
            response = "Username already taken"
            client_socket.sendall(len(response).to_bytes(4, byteorder='big'))
            # Send message
            client_socket.sendall(response.encode())

    def login_function(self, db, message, client_socket, addr):
        ret = '0'
        try:
            user_pas = db.get_user(message[0])
            user_pas = str(user_pas)
            if len(str(user_pas)) > 3:
                if (user_pas.split("'")[1]) == message[1]:
                    response = 'true'
                    self.session.append(Session(addr[0], addr[1], client_socket, message[0]))
                    ret = message[0]
                else:

                    response = 'false'
            else:
                response = 'false'
            # Send message size
            print(f"response: {response}")
            client_socket.sendall(len(response).to_bytes(4, byteorder='big'))
            # Send message
            client_socket.sendall(response.encode(FORMAT))
            print("sucesesfully sent")
        except Exception as e:
            print(f"Error: {e}")
        return ret
        # Func runs when client connect to the room

    def connect_to_the_room(self, message, db, client_socket):
        # Get username
        user = message.pop(-1)
        room = " ".join(message)

        # Sending previous messages in chat to connected user (also poll if he is the first user in room)
        for usr in self.session:
            if (usr.get_log() == user):
                usr.set_room(room)
                messages = f'MSGS {str(db.get_messages(room))}'

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

        if not room in self.roomsNusers:
            self.skip_dict[room] = [0, 0]
            self.Isstreaming[room] = 0
            self.roomsNusers[room] = []
            self.add_port(room)

            thread = threading.Thread(target=self.create_audio_socket, args=(room,))
            thread.start()

        self.skip_dict[room][0] += 1
        msg = f"PORT {str(self.ports[room])}"

        self.send_message(client_socket, msg)

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

    def skip_func(self, room):
        self.skip_dict[room][1] += 1
        if (self.skip_dict[room][1] / self.skip_dict[room][0] >= 0.5):
            self.send_songs_for_vote(room, 0)

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
        try:
            print(songs_list)
        except:
            pass

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
        user = message.pop(-1)
        room = " ".join(message)
        # Deleting user from room
        count = 0

        self.skip_dict[room][0] -= 1


        # Searching that exact user among the session list
        for usr in self.session:
            if (usr.get_log() == user):
                # Setting room variable for the user None
                usr.set_room(None)
            # Counting people in room
            if (usr.get_room == room): count += 1
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if count == 0:
            # If there is no users currently in the room, delete the voting
            for voting in self.votings:
                if voting.get_room() == room:
                    self.votings.remove(voting)
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
    # Generating port for streaming music

    def add_port(self, room):
        port = random.randint(1024, 65535)
        if port not in self.ports.values() and port != self.port:
            self.ports[room] = port
        else: self.add_port(room)


    # Creating audio socket for specific room
    def create_audio_socket(self, room):
        audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        audio_socket.bind(("", self.ports[room]))
        audio_socket.listen(5)
        while True:
            user_audio, addr = audio_socket.accept()
            print("Client connected")
            # If there is no currently stream
            if self.Isstreaming[room] == 0:
                msg = 'FINE'
            # Else we are sending all the data about current song.
            else:
                for voting in self.votings:
                    if voting.get_room() == room:
                        info = voting.get_choosen_song()
                        song = info.split(":::::")[0]
                        song = song.replace("::::", "-")
                        link = info.split(":::::")[-1]
                        msg = f"STREAM {song} {link}"
                        print(msg)
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

    def streaming_current_file(self, room, song_name, link):
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
                self.send_message_to_everybody(room, f"STREAM {song_name} {link}")

                self.Isstreaming[room] = 1
                while True:
                    print("bf sleep")
                    data = wf.readframes(CHUNK_SIZE)
                    print("i hate kfc people")
                    if not data:
                        self.get_recommendations(song, [], self.session, room)
                        break

                    count = 0
                    for audio_socket in self.roomsNusers[room]:
                        try:
                            count += 1
                            print("before send")
                            print(audio_socket)
                            audio_socket.sendall(data)
                            print('after send')

                        except:
                            print("Client disconnected")
                            try:
                                self.roomsNusers[room].remove(audio_socket)
                            except ValueError:
                                print("Client already removed")
                            print("Client removed from the list")
                    print(count)
                    if count == 0:
                        self.Isstreaming[room] = 0
                        return
                    print(f"Sent to {count} clients")

    def download_and_stream_song(self, song_name, artist_name, link, room):
        msg = f"MSG Dj_Arbuzz Downloading the song..."
        for usr in self.session:
            if (usr.get_room() == room):
                # Send message size
                sock = usr.get_sock()
                sock.sendall(len(msg).to_bytes(4, byteorder='big'))
                # Send message
                sock.sendall(msg.encode())

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
            "--ffmpeg-location", "C:/Users/SA/music n chill/ffmpeg/bin"
        ]

        # Run the command
        result = subprocess.run(command, capture_output=True, text=True)

        # Print the output for debugging
        if result.returncode == 0:
            print("Download successful!")
            print(result.stdout)
        else:
            print("Download failed!")
            print(result.stderr)

        # if the room is empty, deleting downloaded song
        if self.count_users(room) == 0:
            folder_path = Path("songs") / room
            if folder_path.exists():
                [file.unlink() for file in folder_path.glob("*") if file.is_file()]
            return
        print("READY!")

        self.streaming_current_file(room, f"{song_name}-{artist_name}", link)

    def start_timer(self, voting):
        db = database()
        chosen_song = voting.start_timer()


        art = chosen_song.split("::::")
        song_name = art.pop(0)
        art = "::::".join(art)
        print(art)
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
        print(f"Song chosen by users: {song_artist}")

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
        message = f"VOTING 4 {room} {response_text}"

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
