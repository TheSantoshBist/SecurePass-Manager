import os
import json
import sqlite3

def init_program_files():
    """Initialize config.json and passwords.db if they don't exist"""
    # Initialize config.json
    if not os.path.exists('config.json'):
        with open('config.json', 'w') as f:
            json.dump({"master_hash": None, "salt": None}, f)

    # Initialize passwords.db and create tables
    if not os.path.exists('passwords.db'):
        conn = sqlite3.connect('passwords.db')
        cursor = conn.cursor()

        # Create passwords table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website TEXT NOT NULL,
                username TEXT NOT NULL,
                password BLOB NOT NULL,
                category TEXT,
                tags TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')

        # Create categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                name TEXT PRIMARY KEY
            )
        ''')

        conn.commit()
        conn.close()