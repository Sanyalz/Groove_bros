import sqlite3
import json
from datetime import datetime
from cryptography.fernet import Fernet

class database:
    def __init__(self, db_name="clients.db"):
        self.db_name = db_name

    def if_user_in_db(self, login):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute("SELECT * FROM clients WHERE login = ?", (login,)).fetchall()
            return bool(len(result))

    def new_user(self, login, password, role):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute("""
                INSERT INTO clients (login, password, Role, IsLogged) 
                VALUES (?, ?, ?, ?)
            """, (login, password, role, 0))
            conn.commit()
            return result

    def get_user_password(self, login):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(
                "SELECT password FROM clients WHERE login = ?", (login,)
            ).fetchone()

            if result is None:
                return None

            return result[0]

    def set_isLogged(self, login, isLogged):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            role = cursor.execute("SELECT Role FROM clients WHERE login = ?", (login,)).fetchone()
            role_value = role[0] if role else None
            if not isLogged and role_value == "Guest":
                self.delete_user(login)
            else:
                cursor.execute("""
                    UPDATE clients
                    SET IsLogged = ?
                    WHERE login = ?
                """, (int(isLogged), login))
                conn.commit()

    def delete_user(self, login):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE login = ?", (login,))
            conn.commit()

    def clear_clients(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients")
            conn.commit()

    def clear_messages(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Messages")
            conn.commit()

    def add_message(self, room, login, message):
        cur_time = datetime.now().strftime("%H:%M")
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute("""
                INSERT INTO Messages (login, message, time, room) 
                VALUES (?, ?, ?, ?)
            """, (login, message, cur_time, room))
            conn.commit()
            return result

    def get_messages(self, room):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute("SELECT Login, Message, Time FROM Messages WHERE Room = ?", (room,)).fetchall()
            return [list(row) for row in result]

    def get_user(self, login):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute("SELECT password FROM clients WHERE login = ?", (login,)).fetchall()
            return result

    def new_room(self, room_name, port, amount_of_people):
        is_downloading = 0
        is_streaming = 0
        is_skip_poll_active = 0
        current_song = None
        skip_poll_list = json.dumps([0, amount_of_people])

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Check if room already exists
            cursor.execute("""
                SELECT 1 FROM Rooms WHERE Room_name = ?
            """, (room_name,))
            room_exists = cursor.fetchone()

            if room_exists:
                # Update existing room
                cursor.execute("""
                    UPDATE Rooms
                    SET port = ?, is_downloading = ?, is_streaming = ?,
                        current_song = ?, is_skip_poll_active = ?, skip_poll_list = ?
                    WHERE Room_name = ?
                """, (port, is_downloading, is_streaming, current_song,
                      is_skip_poll_active, skip_poll_list, room_name))
            else:
                # Insert new room

                # Create key for symmetric encryption
                key = Fernet.generate_key().decode()  # decode to store as TEXT

                cursor.execute("""
                       INSERT INTO Rooms (
                           Room_name, port, is_downloading, is_streaming,
                           current_song, is_skip_poll_active, skip_poll_list, key
                       )
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   """, (room_name, port, is_downloading, is_streaming,
                         current_song, is_skip_poll_active, skip_poll_list, key))

            conn.commit()

    def del_rooms_data(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Rooms")
            conn.commit()


    def set_isDownloading(self, room_name, is_downloading):
        self._update_room_column('is_downloading', room_name, int(is_downloading))

    def set_isStreaming(self, room_name, is_streaming):
        self._update_room_column('is_streaming', room_name, int(is_streaming))

    def set_isSkipPollActive(self, room_name, is_active):
        self._update_room_column('is_skip_poll_active', room_name, int(is_active))

    def set_currentSong(self, room_name, song_info):
        self._update_room_column('current_song', room_name, song_info)

    def set_skipPollList(self, room_name, skip_poll_dict):
        skip_poll_json = json.dumps(skip_poll_dict)
        self._update_room_column('skip_poll_list', room_name, skip_poll_json)

    def _update_room_column(self, column_name, room_name, value):
        allowed = ["is_downloading", "is_streaming", "is_skip_poll_active", "current_song", "skip_poll_list"]
        if column_name not in allowed:
            raise ValueError("Invalid column name")
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE Rooms SET {column_name} = ? WHERE Room_name = ?", (value, room_name))
            conn.commit()

    def _get_single_column(self, column_name, room_name):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {column_name} FROM Rooms WHERE Room_name = ?", (room_name,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_isDownloading(self, room_name):
        return self._get_single_column('is_downloading', room_name)

    def get_key(self, room_name):
        return self._get_single_column('key', room_name)

    def get_isStreaming(self, room_name):
        return self._get_single_column('is_streaming', room_name)

    def get_isSkipPollActive(self, room_name):
        return self._get_single_column('is_skip_poll_active', room_name)

    def get_currentSong(self, room_name):
        return self._get_single_column('current_song', room_name)

    def get_skipPollList(self, room_name):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT skip_poll_list FROM Rooms WHERE Room_name = ?", (room_name,))
            result = cursor.fetchone()
            return json.loads(result[0]) if result and result[0] else None

    def get_port(self, room_name):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT port FROM Rooms WHERE Room_name = ?", (room_name,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_all_ports(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT port FROM Rooms")
            results = cursor.fetchall()
            return [row[0] for row in results]
