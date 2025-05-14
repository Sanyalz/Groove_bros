import sqlite3
import json
from datetime import *


# database class
class database:
    # Init function
    def __init__(self):
        self.conn = sqlite3.connect("clients.db")
        self.cursor = self.conn.cursor()

    # Check, if user in database
    def if_user_in_db(self, login):
        result = self.cursor.execute("SELECT * FROM `clients` WHERE `login` = (?)", (login,)).fetchall()
        return bool(len(result))

    # Add new user function
    def new_user(self, ip, login, password):
        result = self.cursor.execute("""
                INSERT INTO `clients` (ip, login, password) 
                VALUES (?, ?, ?)
            """, (ip, login, password))
        self.conn.commit()
        return result

    def new_room(self, name):
        result = self.cursor.execute("""
                        INSERT INTO `Rooms` (Name) 
                        VALUES (?)
                    """, (name,))
        self.conn.commit()
        return result


    def clear_db(self):
        result = self.cursor.execute("""
                                DELETE FROM Clients
                                """)
        self.conn.commit()

    def add_message(self, room, login, message):
        cur_time = datetime.now()
        cur_time = cur_time.strftime("%H:%M")
        result = self.cursor.execute("""
                       INSERT INTO `Messages` (login, message, time, room) 
                       VALUES (?, ?, ?, ?)
                   """, (login, message, cur_time, room))
        self.conn.commit()
        return result

    def get_messages(self, room):
        result = self.cursor.execute('''
            SELECT Login, Message, Time 
            FROM Messages 
            WHERE Room = ?
        ''', (room,)).fetchall()
        result = [list(row) for row in result]
        return result

    def get_sock_by_log(self, login):
        result = self.cursor.execute("SELECT `socket` FROM `clients` WHERE `login` = ?", (login,)).fetchone()
        return result

    # Get user password by login
    def get_user(self, login):
        result = self.cursor.execute("SELECT `password` FROM `clients` WHERE `login` = ?", (login,)).fetchall()
        return result
