# -*- coding: utf-8 -*-from pydub import AudioSegment

from Client_BL import *
import threading
from PyQt5 import QtGui, QtNetwork, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt

# Default IP and port
SRV_IP = "127.0.0.1"
SRV_PORT = "8822"


class Client_GUI(QtWidgets.QWidget):
    def __init__(self, client, login):
        # Init all the variables
        super().__init__()
        # Set window properties+
        self.setWindowTitle("Groove bros")
        self.setGeometry(0, 0, 2200, 1400)

        # Saving client`s data received from Login
        self.client = client
        self.client_login = login

        # Adding client_gui callbacks
        self.client.add_callbacks(self.new_message_in_chat, self.create_vote,
                                  self.on_vote_selected, self.timer,
                                  self.update_suggestion_buttons, self.new_song_voting,
                                  self.del_button, self.display_song_info)

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
        self.room1_button.resize(400, 150)
        self.room1_button.setStyleSheet("font-size: 35px;")
        self.room1_button.clicked.connect(lambda: self.on_click_room('Rock'))

        # Second room button
        self.room2_button = QtWidgets.QPushButton(self)
        self.room2_button.setText("Rap")
        self.room2_button.move(50, 300)
        self.room2_button.resize(400, 150)
        self.room2_button.setStyleSheet("font-size: 35px;")
        self.room2_button.clicked.connect(lambda: self.on_click_room("Rap"))

        # Third room button
        self.room3_button = QtWidgets.QPushButton(self)
        self.room3_button.setText("Pop")
        self.room3_button.move(50, 550)
        self.room3_button.resize(400, 150)
        self.room3_button.setStyleSheet("font-size: 35px;")
        self.room3_button.clicked.connect(lambda: self.on_click_room("Pop"))

        # Create separate line
        self.line = QtWidgets.QFrame(self)
        self.line.setGeometry(QtCore.QRect(600, -80, 31, 2000))
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
        self.label.setGeometry(QtCore.QRect(1100, 150, 515, 50))

        # Yes button
        self.con_button = QtWidgets.QPushButton(self)
        self.con_button.setText("Yes")
        self.con_button.move(1050, 250)
        self.con_button.resize(200, 75)
        self.con_button.clicked.connect(self.on_click_connect)
        self.con_button.setStyleSheet("font-size: 30px;")

        # Leave button
        self.leave_but = QtWidgets.QPushButton(self)
        self.leave_but.setText("Leave")
        self.leave_but.move(1450, 250)
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
            self.main_layout.setContentsMargins(620, 20, 20, 20)
            self.main_layout.setSpacing(10)

        # Create top panel for song info and leave button
        self.top_panel = QtWidgets.QWidget()
        self.top_panel_layout = QtWidgets.QHBoxLayout(self.top_panel)
        self.top_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.top_panel_layout.setSpacing(20)

        # Album cover container
        self.album_cover = QtWidgets.QLabel()
        self.album_cover.setFixedSize(300, 300)
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

        # Add stretch to push leave button to right
        self.top_panel_layout.addWidget(self.song_info_container)
        self.top_panel_layout.addStretch()

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
        self.top_panel_layout.addWidget(self.leave_button, alignment=QtCore.Qt.AlignTop)

        # Add top panel to main layout
        self.main_layout.addWidget(self.top_panel, alignment=QtCore.Qt.AlignTop)

        # Message area
        self.message_area = QtWidgets.QWidget()
        self.message_area.setStyleSheet("background-color: #f0f0f0; padding: 10px;")
        self.message_area_layout = QtWidgets.QVBoxLayout(self.message_area)
        self.message_area_layout.setAlignment(QtCore.Qt.AlignTop)
        self.message_area_layout.setSpacing(5)

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
        self.client.send(f"CON {self.room} " + self.client_login)

    # Sending user's message from chat to server
    def send_message(self):
        # Get text from input field
        message = self.message_input.text()
        if message:
            self.client.send(f"MSG {self.room} " + self.client_login + " " + message)
            self.message_input.clear()

    # Func which responsible for displaying messages in chat
    def new_message_in_chat(self, msg_list):
        try:
            for message in msg_list:
                login, message = message[0], message[1]
                color = '#E0E0E0'
                if (login == 'Dj_Arbuzz'):
                    color = '#edf2ff'
                    width = "2000"
                else:
                    message = self.split_message(message, 30)
                    width = "800"

                if (self.client_login == login):
                    self.label = QtWidgets.QLabel(message, self)
                    self.label.setAlignment(QtCore.Qt.AlignRight)  # Align the text to the right
                    # Light blue background with padding and rounded corners
                    self.label.setStyleSheet(f"""
                                            background-color: #A3C8E4;  /* Light blue background */
                                            padding: 15px;  /* Add more padding inside the label */
                                            border-radius: 20px;  /* Rounded corners */
                                            font-size: 35px;  /* Increase font size */
                                            max-width: 800px;  /* Increase max width so text stays on one line */

                                        """)

                    # Create a layout for the label inside the widget

                    # Set the layout of the widget to ensure the size is exactly as the label's content

                    self.label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

                    # Add the custom widget to the message area layout
                    self.message_area_layout.addWidget(self.label, alignment=QtCore.Qt.AlignRight)

                    # Clear the input field


                elif (self.last_mes_log == login):

                    self.label = QtWidgets.QLabel(message, self)
                    self.label.setAlignment(QtCore.Qt.AlignLeft)
                    self.label.setStyleSheet(f"""
                                            background-color: {color};  /* Light blue background */
                                            padding: 15px;  /* Add more padding inside the label */
                                            border-radius: 20px;  /* Rounded corners */
                                            font-size: 35px;  /* Increase font size */
                                            max-width: {width}px;  /* Increase max width so text stays on one line */

                                        """)
                    self.label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

                    # Add the custom widget to the message area layout
                    self.message_area_layout.addWidget(self.label, alignment=QtCore.Qt.AlignLeft)
                else:

                    nickname_label = QtWidgets.QLabel(login, self)
                    nickname_label.setStyleSheet("font-size: 20px; color: gray; font-weight: bold;")
                    self.message_area_layout.addWidget(nickname_label, alignment=QtCore.Qt.AlignLeft)

                    message_label = QtWidgets.QLabel(message, self)  # Enable word wrapping for long messages
                    message_label.setAlignment(QtCore.Qt.AlignLeft)  # Align the text to the right
                    message_label.setStyleSheet(f"""
                                                        background-color: {color};  /* Light blue background */
                                                        padding: 15px;  /* Add more padding inside the label */
                                                        border-radius: 20px;  /* Rounded corners */
                                                        font-size: 35px;  /* Increase font size */
                                                        max-width: {width}px;  /* Increase max width so text stays on one line */
                                                    """)

                    # Add the message label to the message area layout
                    self.message_area_layout.addWidget(message_label, alignment=QtCore.Qt.AlignLeft)

                    # Clear the input field after sending the message

                    # Automatically scroll to the bottom of the scroll area

                scrollbar = self.message_area.findChild(QtWidgets.QScrollBar)
                if scrollbar:
                    scrollbar.setValue(scrollbar.maximum())

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
                print(f"Deleting widget: {widget}")  # Debugging
                widget.deleteLater()  # Safely delete the widget

        # Ensure overlay and confirm_frame are properly deleted
        if self.overlay:
            print("Deleting overlay")  # Debugging
            self.overlay.deleteLater()
            self.overlay = None  # Remove reference

        if self.confirm_frame:
            print("Deleting confirm_frame")  # Debugging
            self.confirm_frame.deleteLater()
            self.confirm_frame = None  # Remove reference

        # Process pending events to ensure the UI updates immediately
        QApplication.processEvents()

        # Call voting_window after a short delay to avoid recursion or UI issues
        print("Starting timer to call voting_window")  # Debugging
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
        :param song_names: A list of up to 5 song names to display on the buttons.
        """
        if not song_names or len(song_names) > 5:
            print("The list of song names must contain between 1 and 5 items.")


        for button in self.suggestion_buttons:
            button.setVisible(False)
        print("buttons disabled")

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
        # Nickname label
        self.nickname_label = QtWidgets.QLabel('Dj_Arbuzz', self)
        self.nickname_label.setStyleSheet("font-size: 20px; color: gray; font-weight: bold;")
        self.message_area_layout.addWidget(self.nickname_label, alignment=QtCore.Qt.AlignLeft)


        print("OMG I HATE NIGGERS")
        # Whole message widget
        self.vote_widget = QtWidgets.QWidget(self)
        self.vote_widget.setStyleSheet("""
            QWidget {
                background-color: #edf2ff;  /* Light blue background */
                padding-top: 20px;
                padding-left: -40px;
                border-radius: 30px; 
                max-width: 800px;  
            }
        """)

        # Ensure the widget expands horizontally
        self.vote_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,  # Horizontal policy
            QtWidgets.QSizePolicy.Fixed  # Vertical policy
        )

        # Vertical layout for songs in voting
        self.vote_layout = QtWidgets.QVBoxLayout(self.vote_widget)
        self.vote_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.vote_layout.setSpacing(10)  # Reduce spacing between items in the layout

        # Create vote layout
        self.vote_label = QtWidgets.QLabel("Choose song you would like to be next!", self)
        self.vote_label.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #333333; 
            margin-bottom: 30; 
        """)
        self.vote_layout.addWidget(self.vote_label)
        # Circle buttons list
        self.vote_buttons = []
        # Dictionary for saving progress bar values (song: percentage)
        self.vote_progress_bars = {}
        # Dictionary for labels which are displaying percentage (song: label)
        self.vote_percentages = {}
        # Just creating clone of dictionary with votes
        self.vote_counts = songs_dict

        # Total votes calculation
        total_votes = sum(songs_dict.values())
        print("WE ARE here")
        # Loop for each pair of key:value in songs votes dictionary
        for song, votes in songs_dict.items():
            print("black nigga")
            print(song)
            whole_string = song
            song_name = song.split("::::")[0]
            artist = song.split("::::")[1].split(":::::")[0]
            print(song_name, artist)
            self.voting_option(whole_string, song_name, artist, votes, total_votes)

        # Horizontal layout for "add song button" button
        add_song_layout = QtWidgets.QHBoxLayout()
        self.addsong_button = QtWidgets.QPushButton(self)
        self.addsong_button.setText("+ Add song")
        # Set stylesheet to make the button border and background visible
        self.addsong_button.setStyleSheet("""
            QPushButton {
                font-size: 30px;
                background-color: #c5adff;  /* Green background */
                color: black;               /* White text */  
                border-radius: 20px;        /* Rounded corners */
                padding: 10px;              /* Padding inside the button */
                margin-left: 200px;
                margin-right: 200px;
            }
            QPushButton:hover {
                background-color: #45a049;  /* Darker green on hover */
            }
        """)

        self.addsong_button.clicked.connect(self.on_click_add_song)
        add_song_layout.addWidget(self.addsong_button)
        self.vote_layout.addLayout(add_song_layout)

        # Horizontal layout for timer and total votes labels
        self.last_layout = QtWidgets.QHBoxLayout()
        self.last_layout.setSpacing(10)

        # Add a general votes counter at the end
        self.total_votes_label = QtWidgets.QLabel("Voted: 0", self)
        self.total_votes_label.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            color: #333333;
            margin-top: 20px;
        """)
        self.last_layout.addWidget(self.total_votes_label)

        self.timer_label = QtWidgets.QLabel(self)
        self.timer_label.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            color: #333333;
            margin-top: 20px;
        """)
        self.last_layout.addWidget(self.timer_label)
        if timer != 4:
            self.timer_label.setText(f"Until the end of the voting: {str(timer)}")
            thread = threading.Thread(target=self.client.countdown, args=(timer,))
            thread.start()

        self.vote_layout.addLayout(self.last_layout)

        # Add the vote_widget to the main layout
        self.message_area_layout.addWidget(self.vote_widget, alignment=QtCore.Qt.AlignLeft)

    def voting_option(self, whole_string, song, artist, votes, total_votes):
        # Create container widget for each song option
        song_widget = QtWidgets.QWidget()
        song_layout = QtWidgets.QVBoxLayout(song_widget)
        song_layout.setContentsMargins(0, 0, 0, 0)
        song_layout.setSpacing(5)

        # Horizontal layout for voting elements
        vote_row = QtWidgets.QHBoxLayout()
        vote_row.setSpacing(10)

        # Voting button
        button = QtWidgets.QPushButton()
        button.setFixedSize(30, 30)
        button.setCheckable(True)
        button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 15px;
            }
            QPushButton:checked {
                background-color: blue;
            }
        """)
        button.clicked.connect(lambda _, s=whole_string, b=button: self.on_vote_selected(s, b, 0))
        vote_row.addWidget(button)

        # Song info
        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(2)

        song_label = QtWidgets.QLabel(song)
        song_label.setStyleSheet("font-size: 30px; color: #000000;")

        artist_label = QtWidgets.QLabel(artist)
        artist_label.setStyleSheet("font-size: 20px; color: #666666; margin-top: -10px;")

        text_layout.addWidget(song_label)
        text_layout.addWidget(artist_label)
        vote_row.addLayout(text_layout)

        # Percentage label
        percentage_label = QtWidgets.QLabel("0%")
        percentage_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333333;")
        percentage_label.setVisible(False)
        vote_row.addWidget(percentage_label)

        vote_row.addStretch()
        song_layout.addLayout(vote_row)

        # Progress bar
        progress_bar = QtWidgets.QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(int((votes / total_votes) * 100) if total_votes > 0 else 7)
        progress_bar.setTextVisible(False)
        progress_bar.setStyleSheet("""
            QProgressBar {
                height: 10px;
                background: transparent;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background: #295af0;
                border-radius: 5px;
            }
        """)
        song_layout.addWidget(progress_bar)

        # Store references
        self.vote_buttons.append(button)
        self.vote_progress_bars[whole_string] = progress_bar
        self.vote_percentages[whole_string] = percentage_label
        self.vote_counts[whole_string] = votes

        # Add to main voting layout
        self.vote_layout.insertWidget(1, song_widget)

    def new_song_voting(self, song):
        print("Adding song to voting list")  # Debugging
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
    def display_song_info(self, song_name, album_cover_url):
        """Displays the currently playing song info"""
        try:
            # Update song name
            self.song_name_label.setText(song_name)

            # Load album cover
            self.load_album_cover(album_cover_url)

        except Exception as e:
            print(f"Error in stream_start: {e}")

    # Download the album cover into RAM
    def load_album_cover(self, url):
        """Asynchronously loads album cover from URL"""
        try:
            print(f"Loading album cover from: {url}")
            self.manager = QtNetwork.QNetworkAccessManager()
            self.request = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
            self.reply = self.manager.get(self.request)
            self.reply.finished.connect(self.on_image_loaded)
        except Exception as e:
            print(f"Error starting image load: {e}")
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
                    300, 300,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
                self.album_cover.setPixmap(pixmap)
            else:
                print(f"Error loading image: {self.reply.errorString()}")
                self.set_placeholder_image()
        except Exception as e:
            print(f"Error processing loaded image: {e}")
            self.set_placeholder_image()
        finally:
            self.reply.deleteLater()

    def set_placeholder_image(self):
        """Sets a placeholder image when loading fails"""
        try:
            # Create a simple placeholder
            pixmap = QtGui.QPixmap(300, 300)
            pixmap.fill(QtGui.QColor(200, 200, 200))

            # Add text to placeholder
            painter = QtGui.QPainter(pixmap)
            painter.setPen(QtGui.QColor(100, 100, 100))
            painter.setFont(QtGui.QFont("Arial", 20))
            painter.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, "No Image")
            painter.end()

            self.album_cover.setPixmap(pixmap)
        except Exception as e:
            print(f"Error creating placeholder: {e}")

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
        self.client.send(f"LEV {self.room} " + self.client_login)

    def closeEvent(self, event):
        print('loh')

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
    print("inhallah")  # Debugging
    window = Client_GUI(client, login)
    window.show()
    return window



