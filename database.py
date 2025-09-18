import sqlite3
import hashlib # For securely hashing passwords
from datetime import datetime

def init_db():
    """Initializes the database with users and conversations tables."""
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    # Create a table to store user information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    # Link conversations to a user_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    """Hashes the password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    """Adds a new user to the database."""
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError: # This happens if the username is already taken
        return False
    finally:
        conn.close()

def check_user(username, password):
    """Checks if a user exists and the password is correct."""
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, password_hash FROM users WHERE username = ?", (username,)
    )
    user_data = cursor.fetchone()
    conn.close()
    if user_data and user_data[1] == hash_password(password):
        return user_data[0] # Return the user's ID
    return None

def save_message(user_id, role, content):
    """Saves a message linked to a specific user."""
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO conversations (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, role, content, timestamp)
    )
    conn.commit()
    conn.close()

def load_history(user_id):
    """Loads history for a specific user."""
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM conversations WHERE user_id = ? ORDER BY timestamp ASC",
        (user_id,)
    )
    history = cursor.fetchall()
    conn.close()
    return [{"role": row[0], "parts": [row[1]]} for row in history]