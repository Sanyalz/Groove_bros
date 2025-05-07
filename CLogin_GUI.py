# -*- coding: utf-8 -*-from pydub import AudioSegment

from client_gui import *
# Constants


# Images
BTN_IMAGE = "./Images/GUI - button small.png"
BG_IMAGE = "./Images/GUI - BG Login.png"

# Font
FONT = "Calibri"
FONT_BUTTON = (FONT, 16)


# Class CLoginGui
class CLoginGUI(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.client = Client_BL(SRV_IP, SRV_PORT)
        # Set window properties
        self.setWindowTitle("Login")
        self.setGeometry(500, 500, 700, 400)
        self.sock = self.client.connect()
        self.create_ui()

    # Create UI function
    def create_ui(self):
        # if client connected
        if (self.sock):

            # Guest button
            self.guest_button = QtWidgets.QPushButton("Guest", self)
            self.guest_button.setGeometry(QtCore.QRect(410, 320, 150, 60))
            self.guest_button.setStyleSheet("font-size: 35px;")
            self.guest_button.clicked.connect(self.on_click_guest)

            # LOGIN button
            self.LogIn_button = QtWidgets.QPushButton("Log In", self)
            self.LogIn_button.setGeometry(QtCore.QRect(210, 320, 150, 60))
            self.LogIn_button.setStyleSheet("font-size: 35px;")
            self.LogIn_button.clicked.connect(self.on_click_login)

            # Signup button
            self.Signup_button = QtWidgets.QPushButton("Sign up", self)
            self.Signup_button.setGeometry(QtCore.QRect(20, 320, 150, 60))
            self.Signup_button.setStyleSheet("font-size: 35px;")
            self.Signup_button.clicked.connect(self.on_click_signup)

            # Password enter field
            self.password_enter = QtWidgets.QLineEdit(self)
            self.password_enter.setGeometry(QtCore.QRect(40, 180, 450, 55))
            self.password_enter.setStyleSheet("font-size: 35px;")
            self.password_enter.setEchoMode(QtWidgets.QLineEdit.Password)

            # Username enter field
            self.username_enter = QtWidgets.QLineEdit(self)
            self.username_enter.setGeometry(QtCore.QRect(40, 55, 450, 55))
            self.username_enter.setStyleSheet("font-size: 35px;")

            # Username label
            self.username_label = QtWidgets.QLabel("Username:", self)
            self.username_label.setGeometry(QtCore.QRect(40, 0, 300, 60))
            self.username_label.setStyleSheet("font-size: 30px;")

            # Password label
            self.password_label = QtWidgets.QLabel("Password:", self)
            self.password_label.setGeometry(QtCore.QRect(40, 125, 300, 60))
            self.password_label.setStyleSheet("font-size: 30px;")
        else:
            # If the client is not connected to the server, display error
            self.error_label = QtWidgets.QLabel("Failed to connect to server", self)
            self.error_label.setGeometry(QtCore.QRect(60, 0, 500, 60))
            self.error_label.setStyleSheet("font-size: 40px; color: red;")

            self.close_button = QtWidgets.QPushButton("Close", self)
            self.close_button.setGeometry(QtCore.QRect(200, 220, 300, 60))
            self.close_button.setStyleSheet("font-size: 35px;")
            self.close_button.clicked.connect(self.close)


    def on_click_guest(self):
        self.username_enter.setText('sanek')
        self.password_enter.setText('gg')
        self.on_click_login()

    def on_click_signup(self):
        # Get login and password values from fields
        login = self.username_enter.text().strip()
        password = self.password_enter.text().strip()

        # Remove previous error label if it exists
        if hasattr(self, 'err_msg'):
            self.err_msg.deleteLater()

        # Create error label
        self.err_msg = QtWidgets.QLabel(self)
        self.err_msg.setGeometry(QtCore.QRect(70, 240, 500, 60))
        self.err_msg.setStyleSheet("font-size: 35px; color: red;")
        self.err_msg.show()  # Ensure label is displayed
        self.username_enter.clear()
        self.password_enter.clear()

        # Checking if the fields are empty
        if not login or not password:
            self.err_msg.setText("Fields cannot be empty")

        # Checking if there is spaces in login or password
        elif (" " in login or " " in password):
            self.err_msg.setText("Forbidden symbols")

        else:
            self.send("REG" + " " + login + " " + password)
            # Get message size
            msg_size = int.from_bytes(self.sock.recv(4), byteorder='big')


            # Get message from  client
            msg = self.sock.recv(msg_size).decode(FORMAT)
            self.err_msg.setText(msg)
            if msg == 'Successfully registered':
                self.err_msg.setStyleSheet("font-size: 35px; color: green;")

            else:
                self.err_msg.setStyleSheet("font-size: 35px; color: red;")
            self.err_msg.show()  # Ensure label is displayed
            self.username_enter.clear()
            self.password_enter.clear()

    def on_click_login(self):
        login = self.username_enter.text().strip()
        password = self.password_enter.text().strip()

        print(login, password)

        # Remove previous error label if it exists
        if hasattr(self, 'err_msg'):
            self.err_msg.deleteLater()
        # Create error label
        self.err_msg = QtWidgets.QLabel(self)
        self.err_msg.setGeometry(QtCore.QRect(70, 240, 500, 60))
        self.err_msg.setStyleSheet("font-size: 35px; color: red;")
        self.err_msg.show()  # Ensure label is displayed
        self.username_enter.clear()
        self.password_enter.clear()

        # Checking if the fields are empty
        if not login or not password:
            self.err_msg.setText("Fields cannot be empty")

        # Checking if there is spaces in login or password
        elif (" " in login or " " in password):
            self.err_msg.setText("Forbidden symbols")

        else:
            self.send("LOG" + " " + login + " " + password)
            print("sent")
            # Get message size
            msg_size = int.from_bytes(self.sock.recv(4), byteorder='big')
            # Get message from  client
            msg = self.sock.recv(msg_size).decode(FORMAT)

            print("still alive. message " + msg)
            if(msg == 'true'):
                self.new_window = start(self.client, login)  # ? Store reference
                self.hide()
            else:
                self.err_msg.setText("Wrong password or login")


    def send(self, msg):
        try:
            # Save message size
            self.sock.sendall(len(msg).to_bytes(4, byteorder='big'))
            # Send message
            self.sock.sendall(msg.encode(FORMAT))
            write_to_log(f"[CLIENT_BL] send {self.sock.getsockname()} {msg} ")
            return True
        except Exception as e:
            write_to_log(f"[CLIENT_BL] failed to send_data; error: {e}")
            return False


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CLoginGUI()
    window.show()
    sys.exit(app.exec_())

