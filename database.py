import sqlite3

# Connecting to DB
conn = sqlite3.connect('clients.db')
cursor = conn.cursor()

# Table creation, if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Rooms (
        id INTEGER PRIMARY KEY,
        room TEXT
    );
''')

conn.close()
