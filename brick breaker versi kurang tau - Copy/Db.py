import sqlite3

def init_db():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()

    # Buat tabel user
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        score INTEGER DEFAULT 0
    )
    ''')

    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect('game.db')
