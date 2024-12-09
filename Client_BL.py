import socket
import time
from protocol import *


# Constants
BUFFER_SIZE: int = 1024

# Class Client_BL
class Client_BL:

    # Init function
    def __init__(self, ip, port):
        self.ip = ip
        self.port = int(port)
        self.socket = None
        self.receive_image_flag = None

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
            # Save message size
            self.socket.sendall(len(msg).to_bytes(4, byteorder='big'))
            # Send message
            self.socket.sendall(msg.encode(FORMAT))
            write_to_log(f"[CLIENT_BL] send {self.socket.getsockname()} {msg} " + "kcncrjnjrd")
            return True
        except Exception as e:
            write_to_log(f"[CLIENT_BL] failed to send_data; error: {e}" + "ssssssssssssssss")
            return False

    # Disconnect function