import threading
import socket
from protocol import *

# Constants
SRV_IP = "0.0.0.0"
BUFFER_SIZE: int = 1024


# Class Server_BL
class Server_BL():
    # Init function
    def __init__(self, port):
        self.port = port
        self.server = None
        self.SRV_RUNNING = None

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
                    thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                    thread.start()
                    write_to_log(f"[SERVER] ACTIVE CONNECTION {threading.active_count() - 2}")

        except Exception as e:
            # Handle failure
            write_to_log(f"[Server] failed to set up server {e}")

    # Client handle function, will receive everything from client, and send back
    def handle_client(self, client_socket, addr):
        try:
            # This code run in separate for every client
            write_to_log(f"[SERVER] NEW CONNECTION: {addr} connected")

            connected = True

            while connected:

                # Get message size
                msg_size = int.from_bytes(client_socket.recv(4), byteorder='big')
                # Get message from  client
                msg = client_socket.recv(msg_size).decode(FORMAT)

                write_to_log(f"[SERVER] received message from {addr} - {msg}")

                try:
                    # Create a correct response message for the client
                    msg = msg.split("::")
                    cmd = msg[0]
                    args = msg[1]
                except:
                    cmd = str(msg[0])
                    args = ""


            client_socket.close()
            write_to_log(f"[Server] closed client {addr}")
        except Exception as e:
            print(e)

    # Quit server function
    def quit_server(self):
        self.server.close()
        write_to_log("[SERVER] server is disabled")