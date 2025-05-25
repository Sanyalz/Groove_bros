# -*- coding: utf-8 -*-from pydub import AudioSegment

from Client_BL import *
import threading
from PyQt5 import QtGui, QtNetwork, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt

# Default IP and port
SRV_IP = "10.100.102.120"
SRV_PORT = "8822"


class Client_GUI(QtWidgets.QWidget):
    def __init__(self, client, login):
        # Init all the variables
        super().__init__()
        # Set window properties+
        self.setWindowTitle("Groove bros")

        self.NumberOfUsers = 0
        self.setGeometry(0, 0, 1500, 850)

        # Saving client`s data received from Login
        self.client = client
        self.client_login = login
        self.client.set_login(login)

        self.If_Voted_for_skip = 0


        # Adding client_gui callbacks
        self.client.add_callbacks(self.new_message_in_chat, self.create_vote,
                                  self.on_vote_selected, self.timer,
                                  self.update_suggestion_buttons, self.new_song_voting,
                                  self.del_button, self.display_song_info  , self.new_usr, self.create_skip_poll, self.update_barchart, self.del_skip_poll, self.clear_song_info)

        # Starting thread which listens to server commands
        thread = threading.Thread(target=self.client.receive, args=())
        thread.start()

        # Variable for saving user`s log which sent last message to chat
        self.last_message_log = None

        # Timer for song-searching
        self.search_timer = QTimer(self)
        self.search_timer.setInterval(500)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.find_song_name)
        self.create_ui()

    # Basic UI as user logged in
    def create_ui(self):
        # First room button
        self.room1_button = QtWidgets.QPushButton(self)
        self.room1_button.setText("Rock")
        self.room1_button.move(50, 50)
        self.room1_button.resize(350, 120)
        self.room1_button.setStyleSheet("font-size: 35px;")
        self.room1_button.clicked.connect(lambda: self.on_click_room('Rock'))

        # Second room button
        self.room2_button = QtWidgets.QPushButton(self)
        self.room2_button.setText("Rap")
        self.room2_button.move(50, 300)
        self.room2_button.resize(350, 120)
        self.room2_button.setStyleSheet("font-size: 35px;")
        self.room2_button.clicked.connect(lambda: self.on_click_room("Rap"))

        # Third room button
        self.room3_button = QtWidgets.QPushButton(self)
        self.room3_button.setText("Pop")
        self.room3_button.move(50, 550)
        self.room3_button.resize(350, 120)
        self.room3_button.setStyleSheet("font-size: 35px;")
        self.room3_button.clicked.connect(lambda: self.on_click_room("Pop"))

        # Create separate line
        self.line = QtWidgets.QFrame(self)
        self.line.setGeometry(QtCore.QRect(400, -80, 31, 2000))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

    # When user enters room
    def on_click_room(self, room):
        # Blocking other rooms buttons when user enter the room
        self.room1_button.setEnabled(False)
        self.room2_button.setEnabled(False)
        self.room3_button.setEnabled(False)
        # Saving current room name
        self.room = room
        # Conformation label
        self.label = QtWidgets.QLabel("Connect to the room?", self)
        # Set the font size (optional)
        font = self.label.font()
        # Set the font size
        font.setPointSize(20)
        self.label.setFont(font)

        # Position the text at (100, 100)
        self.label.setGeometry(QtCore.QRect(900, 150, 515, 50))

        # Yes button
        self.con_button = QtWidgets.QPushButton(self)
        self.con_button.setText("Yes")
        self.con_button.move(800, 250)
        self.con_button.resize(200, 75)
        self.con_button.clicked.connect(self.on_click_connect)
        self.con_button.setStyleSheet("font-size: 30px;")

        # Leave button
        self.leave_but = QtWidgets.QPushButton(self)
        self.leave_but.setText("Leave")
        self.leave_but.move(1100, 250)
        self.leave_but.resize(200, 75)
        self.leave_but.clicked.connect(self.on_click_lev)
        self.leave_but.setStyleSheet("font-size: 30px;")

        # Making sure all the labels and buttons displays correctly
        self.label.show()
        self.con_button.show()
        self.leave_but.show()

    # When user leaves the room on confirmation stage
    def on_click_lev(self):
        # Deleting conformation label
        self.label.deleteLater()
        self.con_button.deleteLater()
        self.leave_but.deleteLater()

        # Setting rooms buttons enabled
        self.room1_button.setEnabled(True)
        self.room2_button.setEnabled(True)
        self.room3_button.setEnabled(True)

    # If user clicked "Yes" on confirmation stage
    def on_click_connect(self):
        # Remove the confirmation label and buttons
        self.label.deleteLater()
        self.con_button.deleteLater()
        self.leave_but.deleteLater()

        # the variable we need for right messages in chat classification
        self.last_mes_log = None

        # Clear the existing chat layout if it exists
        if hasattr(self, 'main_layout'):
            self.clear_layout(self.main_layout)
        else:
            # Create the main layout if it doesn't exist
            self.main_layout = QtWidgets.QVBoxLayout(self)
            self.main_layout.setContentsMargins(420, 20, 20, 20)
            self.main_layout.setSpacing(10)

        # Create top panel for song info and leave button
        self.top_panel = QtWidgets.QWidget()
        self.top_panel_layout = QtWidgets.QHBoxLayout(self.top_panel)
        self.top_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.top_panel_layout.setSpacing(20)

        # Album cover container
        self.album_cover = QtWidgets.QLabel()
        self.album_cover.setFixedSize(200, 200)
        self.album_cover.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.top_panel_layout.addWidget(self.album_cover)

        # Song info container
        self.song_info_container = QtWidgets.QWidget()
        self.song_info_layout = QtWidgets.QVBoxLayout(self.song_info_container)
        self.song_info_layout.setContentsMargins(0, 0, 0, 0)
        self.song_info_layout.setSpacing(5)
        self.song_info_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        # Song name label
        self.song_name_label = QtWidgets.QLabel()
        self.song_name_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #333333;
        """)
        self.song_name_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.song_info_layout.addWidget(self.song_name_label)

        # Artist name label
        self.artist_name_label = QtWidgets.QLabel()
        self.artist_name_label.setStyleSheet("""
            font-size: 24px;
            color: #777777;
        """)
        self.artist_name_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.song_info_layout.addWidget(self.artist_name_label)


        # Add stretch to push leave button to right
        self.top_panel_layout.addWidget(self.song_info_container)
        self.top_panel_layout.addStretch()

        # Right-side button container (vertical layout)
        self.right_button_container = QtWidgets.QWidget()
        self.right_button_layout = QtWidgets.QVBoxLayout(self.right_button_container)
        self.right_button_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        self.right_button_layout.setSpacing(10)

        # Right-side button container (vertical layout)
        self.right_button_container = QtWidgets.QWidget()
        self.right_button_layout = QtWidgets.QVBoxLayout(self.right_button_container)
        self.right_button_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        self.right_button_layout.setSpacing(10)

        # Leave button
        self.leave_button = QtWidgets.QPushButton("Leave")
        self.leave_button.setStyleSheet("""
            background-color: #FF4D4D;
            color: white;
            font-size: 30px;
            padding: 8px 15px;
            border-radius: 10px;
        """)
        self.leave_button.setFixedSize(150, 60)
        self.leave_button.clicked.connect(self.leave)
        self.right_button_layout.addWidget(self.leave_button)



        # Add right-side container to top panel layout
        self.top_panel_layout.addWidget(self.right_button_container, alignment=QtCore.Qt.AlignTop)

        # Add right-side container to top panel layout
        self.top_panel_layout.addWidget(self.right_button_container, alignment=QtCore.Qt.AlignTop)

        # Add top panel to main layout
        self.main_layout.addWidget(self.top_panel, alignment=QtCore.Qt.AlignTop)

        # Message area
        self.message_area = QtWidgets.QWidget()
        self.message_area.setStyleSheet("background-color: #f0f0f0; padding: 10px;")
        self.message_area_layout = QtWidgets.QVBoxLayout(self.message_area)
        self.message_area_layout.setAlignment(QtCore.Qt.AlignTop)
        self.message_area_layout.setSpacing(1)

        # Scroll area
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.message_area)
        self.main_layout.addWidget(self.scroll_area)

        # Input area
        self.message_input = QtWidgets.QLineEdit()
        self.message_input.setPlaceholderText("Enter message...")
        self.message_input.setStyleSheet("""
            font-size: 35px;
            padding: 10px;
            border-radius: 10px;
        """)
        self.message_input.setMinimumHeight(75)
        self.message_input.setMinimumWidth(200)

        # Send button
        self.send_button = QtWidgets.QPushButton("Send")
        self.send_button.setStyleSheet("""
            font-size: 35px;
            padding: 10px 20px;
            border-radius: 10px;
            background-color: #5DB075;
        """)
        self.send_button.setMinimumHeight(75)
        self.send_button.setMinimumWidth(100)
        self.send_button.clicked.connect(self.send_message)

        # Layout with enter field, and send button
        self.input_layout = QtWidgets.QHBoxLayout()
        self.input_layout.addWidget(self.message_input)
        self.input_layout.addWidget(self.send_button)
        self.main_layout.addLayout(self.input_layout)

        self.setLayout(self.main_layout)
        self.find_song_func()
        # Sending the message to server
        self.client.send(f"CON {self.room} {self.client_login} {self.client.get_public_key()}")
    def new_usr(self, num):
        self.NumberOfUsers += int(num)

    def skip_song(self):
        self.create_skip_poll()
    # Sending user's message from chat to server
    def send_message(self):
        # Get text from input field
        message = self.message_input.text()
        if message:
            message = self.client.encrypt_message(message)
            self.client.send(f"MSG {self.room} {self.client_login} {message}")
            self.message_input.clear()


    # Func which responsible for displaying messages in chat
    def new_message_in_chat(self, msg_list):
        try:
            for message in msg_list:
                login, message = message[0], message[1]
                color = '#E0E0E0'
                if login == 'Dj_Arbuzz':
                    color = '#edf2ff'
                    width = "1200"  # Slightly larger for DJ if needed
                else:
                    message = self.split_message(message, 30)
                    width = "600"

                if self.client_login == login:
                    self.label = QtWidgets.QLabel(message, self)
                    self.label.setAlignment(QtCore.Qt.AlignRight)
                    self.label.setStyleSheet(f"""
                        background-color: #A3C8E4;
                        padding: 8px;
                        border-radius: 12px;
                        font-size: 20px;
                        max-width: {width}px;
                    """)
                    self.label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                    self.message_area_layout.addWidget(self.label, alignment=QtCore.Qt.AlignRight)

                elif self.last_mes_log == login:
                    self.label = QtWidgets.QLabel(message, self)
                    self.label.setAlignment(QtCore.Qt.AlignLeft)
                    self.label.setStyleSheet(f"""
                        background-color: {color};
                        padding: 8px;
                        border-radius: 12px;
                        font-size: 20px;
                        max-width: {width}px;
                    """)
                    self.label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                    self.message_area_layout.addWidget(self.label, alignment=QtCore.Qt.AlignLeft)

                else:
                    nickname_label = QtWidgets.QLabel(login, self)
                    nickname_label.setStyleSheet("font-size: 14px; color: gray; font-weight: bold;")
                    self.message_area_layout.addWidget(nickname_label, alignment=QtCore.Qt.AlignLeft)

                    message_label = QtWidgets.QLabel(message, self)
                    message_label.setAlignment(QtCore.Qt.AlignLeft)
                    message_label.setStyleSheet(f"""
                        background-color: {color};
                        padding: 8px;
                        border-radius: 12px;
                        font-size: 20px;
                        max-width: {width}px;
                    """)
                    self.message_area_layout.addWidget(message_label, alignment=QtCore.Qt.AlignLeft)


                # Scroll to the bottom
                QtCore.QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(
                    self.scroll_area.verticalScrollBar().maximum()))

                self.last_mes_log = login
        except:
            pass

    '''NEXT FUNCTIONS ARE RESPONSIBLE FOR VOTING OPERATIONS'''

    # Function
    def find_song_func(self):
        # Overlay
        self.overlay = QWidget(self)
        self.overlay.setGeometry(self.rect())
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 150);")  # Semi-transparent gray
        self.overlay.setVisible(False)

        # Confirmation Frame
        self.confirm_frame = QFrame(self)
        self.confirm_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #cccccc;
            }
        """)
        self.confirm_frame.setFixedSize(750, 460)  # Increased height to accommodate suggestion buttons
        self.confirm_frame.setFrameShape(QFrame.Box)
        self.confirm_frame.setFrameShadow(QFrame.Raised)
        self.confirm_frame.move((self.width() - 750) // 2, (self.height() - 460) // 2)  # Centering the frame
        self.confirm_frame.setVisible(False)

        # Layout for the confirmation frame
        self.confirm_frame_layout = QVBoxLayout(self.confirm_frame)
        self.confirm_frame_layout.setAlignment(Qt.AlignCenter)
        self.confirm_frame_layout.setSpacing(20)  # Add spacing between widgets

        # Label
        self.confirm_label = QLabel("Enter the name of the song + artist:", self.confirm_frame)
        self.confirm_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333333;
                border: none;
            }
        """)
        self.confirm_label.setAlignment(Qt.AlignCenter)
        self.confirm_frame_layout.addWidget(self.confirm_label)

        # Input field
        self.song_enter = QtWidgets.QLineEdit(self.confirm_frame)
        self.song_enter.setStyleSheet("""
            QLineEdit {
                font-size: 20px;
                padding: 10px;
                border: 2px solid #cccccc;
                border-radius: 10px;
                background-color: #f9f9f9;
                font-size: 24px;
            }
            QLineEdit:focus {
                border: 2px solid #000000;
                background-color: #ffffff;
            }
        """)
        self.song_enter.textChanged.connect(self.on_text_changed)
        self.song_enter.setAlignment(Qt.AlignCenter)
        self.song_enter.setFixedWidth(600)  # Set a fixed width for the input field
        self.confirm_frame_layout.addWidget(self.song_enter)

        # Suggestion Buttons (initially invisible)
        self.suggestion_buttons = []
        self.suggestions_layout = QVBoxLayout()  # Vertical layout for suggestion buttons
        self.suggestions_layout.setAlignment(Qt.AlignCenter)
        self.suggestions_layout.setSpacing(10)  # Spacing between buttons

        for _ in range(5):
            button = QPushButton("", self.confirm_frame)
            button.setFixedSize(600, 40)  # Same width as QLineEdit
            button.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    padding: 5px;
                    background-color: #e0e0e0;
                    color: #333333;
                    border-radius: 5px;
                    border: 1px solid #cccccc;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
                QPushButton:pressed {
                    background-color: #c0c0c0;
                }
            """)
            button.setVisible(False)  # Initially hidden
            button.clicked.connect(self.send_song)
            self.suggestion_buttons.append(button)
            self.suggestions_layout.addWidget(button)

        self.confirm_frame_layout.addLayout(self.suggestions_layout)

        # Buttons container
        self.buttons_container = QWidget(self.confirm_frame)
        self.buttons_layout = QtWidgets.QHBoxLayout(self.buttons_container)  # Use QHBoxLayout for side-by-side buttons
        self.buttons_layout.setAlignment(Qt.AlignCenter)
        self.buttons_layout.setSpacing(80)  # Add spacing between buttons

        # Cancel Button
        self.cancel_button = QPushButton("Cancel", self.buttons_container)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 10px 20px;
                background-color: #f44336;
                color: white;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
            QPushButton:pressed {
                background-color: #c62828;
            }
        """)
        self.cancel_button.clicked.connect(self.cancel_func)
        self.buttons_layout.addWidget(self.cancel_button)

        self.confirm_frame_layout.addWidget(self.buttons_container)

    def cancel_func(self):
        print("Cancel function called")  # Debugging

        # Hide the overlay and confirmation frame
        self.overlay.setVisible(False)
        self.confirm_frame.setVisible(False)

        # Clear the song input field
        self.song_enter.clear()

        # Hide all suggestion buttons
        for button in self.suggestion_buttons:
            button.setVisible(False)

        # Clear the confirm_frame_layout by removing all widgets
        while self.confirm_frame_layout.count():
            item = self.confirm_frame_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()  # Safely delete the widget

        # Ensure overlay and confirm_frame are properly deleted
        if self.overlay:
            self.overlay.deleteLater()
            self.overlay = None  # Remove reference

        if self.confirm_frame:
            self.confirm_frame.deleteLater()
            self.confirm_frame = None  # Remove reference

        # Process pending events to ensure the UI updates immediately
        QApplication.processEvents()

        # Call voting_window after a short delay to avoid recursion or UI issues
        self.find_song_func()

    def send_song(self):
        button = self.sender()
        msg = f"ADD_SONG {self.room} {button.property("song_name")}::::{button.property("song_artist")}:::::{button.property("cover_url")}"
        self.cancel_func()
        self.client.send(msg)
        self.del_button()

    def del_button(self):
        self.addsong_button.deleteLater()


    def update_suggestion_buttons(self, song_names):

        """
        Update the suggestion buttons with a list of song names.
        A list of up to 5 song names to display on the buttons.
        """


        for button in self.suggestion_buttons:
            button.setVisible(False)

        i = 0
        for song in song_names:
            art = song.split("::::")
            song_name = art.pop(0)
            art = "::::".join(art)
            song_artist = art.split(":::::")[0]
            link = art.split(":::::")[-1]
            self.suggestion_buttons[i].setText(f"{song_name} - {song_artist}")
            self.suggestion_buttons[i].setProperty("cover_url", link)
            self.suggestion_buttons[i].setProperty("song_name", song_name)
            self.suggestion_buttons[i].setProperty("song_artist", song_artist)
            self.suggestion_buttons[i].setVisible(True)
            i+=1

    def on_text_changed(self):

        if self.search_timer.isActive():
            self.search_timer.stop()
        self.search_timer.start()

    def find_song_name(self):
        song = self.song_enter.text()
        if len(song) > 2:
            self.client.send(f"FIND_SONG {song}")
        else:
            for button in self.suggestion_buttons:
                button.setText('')
                button.setVisible(False)

    def create_vote(self, songs_dict, timer):
        attrs = [
            "vote_widget", "nickname_label", "vote_layout",
            "vote_label", "vote_buttons", "vote_progress_bars",
            "vote_percentages", "addsong_button", "last_layout",
            "total_votes_label", "timer_label"
        ]
        for attr in attrs:
            if hasattr(self, attr):
                widget = getattr(self, attr)
                try:
                    if isinstance(widget, QtWidgets.QWidget):
                        widget.deleteLater()
                    elif isinstance(widget, (list, dict)):
                        for item in widget.values() if isinstance(widget, dict) else widget:
                            if isinstance(item, QtWidgets.QWidget):
                                item.deleteLater()
                except Exception as e:
                    print(f"Failed to delete {attr}: {e}")
                delattr(self, attr)
        self.nickname_label = QtWidgets.QLabel('Dj_Arbuzz', self)
        self.nickname_label.setStyleSheet("font-size: 14px; color: gray; font-weight: bold;")
        self.message_area_layout.addWidget(self.nickname_label, alignment=QtCore.Qt.AlignLeft)

        self.vote_widget = QtWidgets.QWidget(self)
        self.vote_widget.setStyleSheet("""
            QWidget {
                background-color: #edf2ff;
                padding: 10px;
                border-radius: 15px;
                max-width: 600px;
            }
        """)
        self.vote_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        self.vote_layout = QtWidgets.QVBoxLayout(self.vote_widget)
        self.vote_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.vote_layout.setSpacing(6)

        self.vote_label = QtWidgets.QLabel("Choose song you would like to be next!", self)
        self.vote_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333333;
            margin-bottom: 10px;
        """)
        self.vote_layout.addWidget(self.vote_label)

        self.vote_buttons = []
        self.vote_progress_bars = {}
        self.vote_percentages = {}
        self.vote_counts = songs_dict
        total_votes = sum(songs_dict.values())

        for song, votes in songs_dict.items():
            song_name = song.split("::::")[0]
            artist = song.split("::::")[1].split(":::::")[0]
            self.voting_option(song, song_name, artist, votes, total_votes)

        add_song_layout = QtWidgets.QHBoxLayout()
        self.addsong_button = QtWidgets.QPushButton(self)
        self.addsong_button.setText("+ Add song")
        self.addsong_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                background-color: #c5adff;
                color: black;
                border-radius: 12px;
                padding: 6px;
                margin-left: 100px;
                margin-right: 100px;
            }
            QPushButton:hover {
                background-color: #a48cff;
            }
        """)
        self.addsong_button.clicked.connect(self.on_click_add_song)
        add_song_layout.addWidget(self.addsong_button)
        self.vote_layout.addLayout(add_song_layout)

        self.last_layout = QtWidgets.QHBoxLayout()
        self.last_layout.setSpacing(8)

        self.total_votes_label = QtWidgets.QLabel("Voted: 0", self)
        self.total_votes_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333333;
        """)
        self.last_layout.addWidget(self.total_votes_label)

        self.timer_label = QtWidgets.QLabel(self)
        self.timer_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333333;
        """)
        self.last_layout.addWidget(self.timer_label)
        if timer != 4:
            self.timer_label.setText(f"Until the end of the voting: {str(timer)}")
            thread = threading.Thread(target=self.client.countdown, args=(timer,))
            thread.start()

        self.vote_layout.addLayout(self.last_layout)
        self.message_area_layout.addWidget(self.vote_widget, alignment=QtCore.Qt.AlignLeft)

        # Scroll to the bottom
        QtCore.QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()))

    def voting_option(self, whole_string, song, artist, votes, total_votes):
        song_widget = QtWidgets.QWidget()
        song_layout = QtWidgets.QVBoxLayout(song_widget)
        song_layout.setContentsMargins(0, 0, 0, 0)
        song_layout.setSpacing(4)

        vote_row = QtWidgets.QHBoxLayout()
        vote_row.setSpacing(6)

        button = QtWidgets.QPushButton()
        button.setFixedSize(20, 20)  # Equal width and height for a perfect circle
        button.setCheckable(True)
        button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 12px;
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:checked {
                background-color: blue;
                border: none;
            }
        """)

        button.clicked.connect(lambda _, s=whole_string, b=button: self.on_vote_selected(s, b, 0))
        vote_row.addWidget(button)

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(1)

        song_label = QtWidgets.QLabel(song)
        song_label.setStyleSheet("font-size: 16px; color: #000000;")

        artist_label = QtWidgets.QLabel(artist)
        artist_label.setStyleSheet("font-size: 12px; color: #666666;")

        text_layout.addWidget(song_label)
        text_layout.addWidget(artist_label)
        vote_row.addLayout(text_layout)

        percentage_label = QtWidgets.QLabel("0%")
        percentage_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333;")
        percentage_label.setVisible(False)
        vote_row.addWidget(percentage_label)

        vote_row.addStretch()
        song_layout.addLayout(vote_row)

        progress_bar = QtWidgets.QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(int((votes / total_votes) * 100) if total_votes > 0 else 2)
        progress_bar.setTextVisible(False)
        progress_bar.setStyleSheet("""
            QProgressBar {
                height: 6px;
                background: transparent;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: #295af0;
                border-radius: 3px;
            }
        """)
        song_layout.addWidget(progress_bar)

        self.vote_buttons.append(button)
        self.vote_progress_bars[whole_string] = progress_bar
        self.vote_percentages[whole_string] = percentage_label
        self.vote_counts[whole_string] = votes

        self.vote_layout.insertWidget(1, song_widget)

    def new_song_voting(self, song):
        votes = 0
        total_votes = int(self.total_votes_label.text().split(" ")[-1])  # Get current total votes
        art = song.split("::::")
        song_name = art.pop(0)
        art = "::::".join(art)
        song_artist = art.split(":::::")[0]
        link = art.split(":::::")[-1]
        self.voting_option(song, song_name, song_artist, votes, total_votes)

    def on_click_add_song(self):
        self.overlay.setVisible(True)
        self.confirm_frame.setVisible(True)

        # Center the confirmation frame
        self.confirm_frame.move(
            (self.width() - self.confirm_frame.width()) // 2,
            (self.height() - self.confirm_frame.height()) // 2
        )



    # When user voted
    def on_vote_selected(self, song, button, status):
        try:
            if status == 0:  # User-initiated vote
                self.client.send(f"VOTE {self.room} {self.client_login} {song}")
                for btn in self.vote_buttons:
                    btn.setEnabled(False)
                button.setChecked(True)

            # Update vote count
            self.vote_counts[song] = self.vote_counts.get(song, 0) + 1

            # Start timer if first vote
            if sum(self.vote_counts.values()) == 1:
                self.timer_label.setText("Until the end of the voting: 4")
                threading.Thread(target=self.client.countdown, args=(4,)).start()

            # Update UI
            self.update_vote_display()

        except Exception as e:
            print(f"Vote error: {e}")

    def update_vote_display(self):
        total_votes = sum(self.vote_counts.values())
        self.total_votes_label.setText(f"Voted: {total_votes}")

        for song, progress_bar in self.vote_progress_bars.items():
            votes = self.vote_counts.get(song, 0)
            percent = int((votes / total_votes) * 100) if total_votes > 0 else 0

            progress_bar.setValue(percent)
            if song in self.vote_percentages:
                self.vote_percentages[song].setText(f"{percent}%")
                self.vote_percentages[song].setVisible(total_votes > 0)

    # When server starts to stream the song, that function runs and displays song's info and album cover
    def display_song_info(self, artist, song_name, album_cover_url):
        """Displays the currently playing song info"""
        try:
            # Update song and artist name
            self.song_name_label.setText(song_name)
            self.artist_name_label.setText(artist)

            # Load album cover
            self.load_album_cover(album_cover_url)

        except Exception as e:
            print(f"Error in stream_start: {e}")

    def clear_song_info(self):
        self.del_skip_poll()
        """Clears the album cover and song name display."""
        try:
            self.song_name_label.setText("")
            self.artist_name_label.setText("")

            blank_pixmap = QtGui.QPixmap(200, 200)
            blank_pixmap.fill(QtGui.QColor(240, 240, 240))  # light gray
            self.album_cover.setPixmap(blank_pixmap)

            print("Cleared song info.")
        except Exception as e:
            print(f"Error clearing song info: {e}")

    # Download the album cover into RAM
    def load_album_cover(self, url):
        """Asynchronously loads album cover from URL"""
        try:
            self.manager = QtNetwork.QNetworkAccessManager()
            self.request = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
            self.reply = self.manager.get(self.request)
            self.reply.finished.connect(self.on_image_loaded)
        except Exception as e:
            self.set_placeholder_image()

    # As image downloaded, that func runs
    def on_image_loaded(self):
        """Callback when image finishes loading"""
        try:
            if self.reply.error() == QtNetwork.QNetworkReply.NoError:
                data = self.reply.readAll()
                image = QtGui.QImage()
                image.loadFromData(data)
                pixmap = QtGui.QPixmap.fromImage(image).scaled(
                    200, 200,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
                self.album_cover.setPixmap(pixmap)
            else:
                self.set_placeholder_image()
        except Exception as e:
            self.set_placeholder_image()
        finally:
            self.reply.deleteLater()

    def set_placeholder_image(self):
        """Sets a placeholder image when loading fails"""
        try:
            # Create a simple placeholder
            pixmap = QtGui.QPixmap(200, 200)
            pixmap.fill(QtGui.QColor(200, 200, 200))

            # Add text to placeholder
            painter = QtGui.QPainter(pixmap)
            painter.setPen(QtGui.QColor(100, 100, 100))
            painter.setFont(QtGui.QFont("Arial", 20))
            painter.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, "No Image")
            painter.end()

            self.album_cover.setPixmap(pixmap)
        except Exception as e:
            pass

    # Function which called every second as the timer begins
    def timer(self):
        try:
            timer = int(self.timer_label.text().split(" ")[-1])
            timer -= 1
            if timer == 0:
                if hasattr(self, "vote_widget"):
                    self.vote_widget.deleteLater()
                if hasattr(self, "nickname_label"):
                    self.nickname_label.deleteLater()

                # Create QLabel to display the message
            self.timer_label.setText(f"Until the end of the voting: {timer}")
        except:
            pass







    # SKIP SONG POLL

    def create_skip_poll(self):
        # Nickname label
        self.nickname_label = QtWidgets.QLabel('Dj_Arbuzz', self)
        self.nickname_label.setStyleSheet("font-size: 14px; color: gray; font-weight: bold;")
        self.message_area_layout.addWidget(self.nickname_label, alignment=QtCore.Qt.AlignLeft)

        # Poll container
        self.skip_widget = QtWidgets.QWidget(self)
        self.skip_widget.setStyleSheet("""
            QWidget {
                background-color: #edf2ff;
                padding: 10px;
                border-radius: 15px; 
                max-width: 600px;  
            }
        """)
        self.skip_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed
        )

        # Poll layout
        self.skip_layout = QtWidgets.QVBoxLayout(self.skip_widget)
        self.skip_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.skip_layout.setSpacing(6)

        # Poll question
        self.skip_label = QtWidgets.QLabel("Skip to the next song?", self)
        self.skip_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333333; 
            margin-bottom: 10px; 
        """)
        self.skip_layout.addWidget(self.skip_label)

        # Voting data
        self.skip_votes = {"Yes": 0, "No": self.NumberOfUsers}
        self.skip_buttons = []
        self.skip_progress_bars = {}
        self.skip_percentages = {}

        # Create poll option(s)
        self.create_skip_option("Yes", "Yes", 0)

        # Add poll widget to layout
        self.message_area_layout.addWidget(self.skip_widget, alignment=QtCore.Qt.AlignLeft)

        # Scroll to the bottom
        QtCore.QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()))

    def create_skip_option(self, option_id, option_text, votes):
        # Container widget
        option_widget = QtWidgets.QWidget()
        option_layout = QtWidgets.QVBoxLayout(option_widget)
        option_layout.setContentsMargins(0, 0, 0, 0)
        option_layout.setSpacing(4)

        # Voting row
        vote_row = QtWidgets.QHBoxLayout()
        vote_row.setSpacing(6)

        # Vote button
        self.skip_button = QtWidgets.QPushButton()
        self.skip_button.setFixedSize(20, 20)  # Equal width and height for a perfect circle
        self.skip_button.setCheckable(True)
        self.skip_button.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        border: 2px solid #3498db;
                        border-radius: 12px;
                        min-width: 20px;
                        max-width: 20px;
                        min-height: 20px;
                        max-height: 20px;
                        padding: 0px;
                        margin: 0px;
                    }
                    QPushButton:checked {
                        background-color: blue;
                        border: none;
                    }
                """)
        self.skip_button.clicked.connect(self.on_skip_vote_selected)
        vote_row.addWidget(self.skip_button)

        # Option label
        option_label = QtWidgets.QLabel(option_text)
        option_label.setStyleSheet("font-size: 16px; color: #000000;")
        vote_row.addWidget(option_label)

        # Percentage label
        self.percentage_label = QtWidgets.QLabel("0%")
        self.percentage_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333;")
        self.percentage_label.setVisible(True)
        vote_row.addWidget(self.percentage_label)

        vote_row.addStretch()
        option_layout.addLayout(vote_row)

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                height: 6px;
                background: transparent;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: #295af0;
                border-radius: 3px;
            }
        """)
        option_layout.addWidget(self.progress_bar)


        # Add to poll layout
        self.skip_layout.insertWidget(1, option_widget)

    def on_skip_vote_selected(self):
        self.skip_button.setChecked(True)
        self.skip_button.setEnabled(False)
        self.If_Voted_for_skip = 1
        self.client.send(f"SKIP {self.room}")


    def update_barchart(self, voted, all_users):
        percentage = int(voted/all_users * 100)

        self.progress_bar.setValue(int(percentage))
        self.percentage_label.setText(f"{int(percentage)}%")
        self.percentage_label.setVisible(True)


    def del_skip_poll(self):
        # Safely delete skip_widget if it exists and is not None
        if hasattr(self, "skip_widget") and self.skip_widget is not None:
            try:
                self.skip_widget.deleteLater()
                self.skip_widget = None
            except Exception as e:
                print(f"Error while deleting skip_widget: {e}")

        # Safely delete nickname_label if it exists and is not None
        if hasattr(self, "nickname_label") and self.nickname_label is not None:
            try:
                self.nickname_label.deleteLater()
                self.nickname_label = None
            except Exception as e:
                pass

        # Reset skip vote flag
        self.If_Voted_for_skip = 0

    def leave(self):
        """
        Clears the chat interface and restores the room selection buttons.
        """


        # Clear the chat-related widgets
        self.clear_layout(self.main_layout)  # Clear the main layout (chat area, input field, etc.)

        # Restore the initial room selection buttons
        self.room1_button.setEnabled(True)
        self.room2_button.setEnabled(True)
        self.room3_button.setEnabled(True)

        # Show the vertical line separator
        self.line.show()

        self.client.leave_the_room()
        # Notify the server that the user has left the room

        self.client.send(f"LEV {self.room} {self.client_login} {self.If_Voted_for_skip}")

    # Window was closed by using red cross
    def closeEvent(self, event):
        self.client.send("BYE")

    def clear_layout(self, layout):
        """
        Recursively clears all widgets inside a layout.
        """
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()  # Remove and delete the widget
            elif item.layout():
                self.clear_layout(item.layout())  # Recursively clear nested layouts

    def close(self):
        self.client.send('DEL Rock ' + self.client_login)
        self.root.destroy()


    def split_message(self, message, max_length):
        words = message.split()
        lines = []
        current_line = ""

        for word in words:
            if len(word) > max_length:

                while len(word) > max_length:
                    if len(current_line) > 0:
                        lines.append(current_line.strip())
                        current_line = ""
                    lines.append(word[:max_length])
                    word = word[max_length:]
                current_line += word + " "
            elif len(current_line) + len(word) + 1 <= max_length:

                current_line += word + " "
            else:

                lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            lines.append(current_line.strip())

        return "\n".join(lines)

    def receive_msg(self):
        pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.send_message()


def start(client, login):
    window = Client_GUI(client, login)
    window.show()
    return window


