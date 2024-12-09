import sqlite3

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

    # Get user info by id
    def get_user(self, id):
        result = self.cursor.execute("SELECT * FROM `clients` WHERE `id` = ?", (id,)).fetchall()
        return result
