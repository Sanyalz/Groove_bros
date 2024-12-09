import threading
from db import *
from protocol import *


# Constants
SRV_IP = "0.0.0.0"
BUFFER_SIZE: int = 1024


# Class Server_BL
class Server_BL():
    # Init function
    def __init__(self, port, client_callback, message_callback):
        self.port = port

        self.db = None
        self.client_callback = client_callback
        '''
        self.delete_callback = delete_client_callback
        self.reg_callback = reg_callback'''
        self.message_callback = message_callback
        self.server = None
        self.SRV_RUNNING = None
        #self.protocol_26 = protocol()

    def set_server_running_flag(self, flag):
        self.SRV_RUNNING = flag

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
        try:
            self.db = database()
            # This code run in separate for every client
            write_to_log(f"[SERVER] NEW CONNECTION: {addr} connected")

            connected = True

            while connected:

                # Get message size
                msg_size = int.from_bytes(client_socket.recv(4), byteorder='big')
                # Get message from  client
                msg = client_socket.recv(msg_size).decode(FORMAT)
                print("полученно: " + msg)
                self.message_callback(msg)
                cmd = msg.split(' ')[0]
                if(cmd == "REG"):
                    if (self.db.if_user_in_db(msg.split(" ")[1]) == False):
                        # Add new user
                        self.db.new_user(client_socket, msg.split(" ")[1], msg.split(" ")[2])
                        client_socket.sendall(b'TEXT')
                        # Send message size
                        response = "Successfully registered"
                        client_socket.sendall(len(response).to_bytes(4, byteorder='big'))
                        # Send message
                        client_socket.sendall(response.encode())
                    else:
                        client_socket.sendall(b'TEXT')
                        # Send message size
                        response = "Username already taken"
                        client_socket.sendall(len(response).to_bytes(4, byteorder='big'))
                        # Send message
                        client_socket.sendall(response.encode())
                elif cmd == "MSG":
                    pass

                '''if(msg.split(' ')[0] == '/song'):
                    response = song_url.get_song_url(msg.split(' ')[1])
                    client_socket.sendall(b'TEXT')
                    # Send message size
                    client_socket.sendall(len(response).to_bytes(4, byteorder='big'))
                    # Send message
                    client_socket.sendall(response.encode())'''

                write_to_log(f"[SERVER] received message from {addr} - {msg}")

        except Exception as ex:
            self.message_callback(f"Failed to receive message: {ex}")

    # Quit server function
    def quit_server(self):
        self.server.close()
        #write_to_log("[SERVER] server is disabled")
