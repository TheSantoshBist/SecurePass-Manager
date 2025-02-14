
import sqlite3
from datetime import datetime
from utils.encryption import Encryptor
from sqlite3 import Connection
from functools import lru_cache

class DatabaseManager:
    _connection_pool = {}

    def __init__(self, master_key: str):
        self.db_path = 'passwords.db'
        self.encryptor = Encryptor(master_key)
        self.conn = self._get_connection()
        self._init_db()

    def _get_connection(self) -> Connection:
        # Reuse existing connection if available
        if self.db_path in self._connection_pool:
            return self._connection_pool[self.db_path]

        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = DELETE")  # Set journal_mode to DELETE
        conn.execute("PRAGMA synchronous = NORMAL")  # Faster synchronization
        conn.execute("PRAGMA cache_size = -2000")  # 2MB cache

        self._connection_pool[self.db_path] = conn
        return conn

    def _init_db(self):
        cursor = self.conn.cursor()
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

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                name TEXT PRIMARY KEY
            )
        ''')
        self.conn.commit()

    def add_password(self, website: str, username: str, password: str,
                    category: str = None, tags: str = None) -> bool:
        encrypted_pass = self.encryptor.encrypt(password)
        timestamp = datetime.now().isoformat()

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO passwords (website, username, password, category,
                                 tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (website, username, encrypted_pass, category, tags,
             timestamp, timestamp))
        self.conn.commit()
        return True

    def get_password(self, id: int) -> dict:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM passwords WHERE id = ?', (id,))
        row = cursor.fetchone()

        if row:
            return {
                'id': row[0],
                'website': row[1],
                'username': row[2],
                'password': self.encryptor.decrypt(row[3]),
                'category': row[4],
                'tags': row[5],
                'created_at': row[6],
                'updated_at': row[7]
            }
        return None

    def search_passwords(self, query: str) -> list:
        cursor = self.conn.cursor()
        # Updated search query to be case-insensitive and search in more fields
        cursor.execute('''
            SELECT * FROM passwords
            WHERE LOWER(website) LIKE LOWER(?)
               OR LOWER(username) LIKE LOWER(?)
               OR LOWER(category) LIKE LOWER(?)
               OR LOWER(tags) LIKE LOWER(?)
            ORDER BY updated_at DESC
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'website': row[1],
                'username': row[2],
                'password': self.encryptor.decrypt(row[3]),
                'category': row[4],
                'tags': row[5],
                'created_at': row[6],
                'updated_at': row[7]
            })
        return results

    def get_all_passwords(self) -> list:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM passwords ORDER BY updated_at DESC')

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'website': row[1],
                'username': row[2],
                'password': self.encryptor.decrypt(row[3]),
                'category': row[4],
                'tags': row[5],
                'created_at': row[6],
                'updated_at': row[7]
            })
        return results

    def update_password(self, id: int, **kwargs) -> bool:
        timestamp = datetime.now().isoformat()
        if 'password' in kwargs:
            kwargs['password'] = self.encryptor.encrypt(kwargs['password'])

        cursor = self.conn.cursor()
        update_fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        query = f'UPDATE passwords SET {update_fields}, updated_at = ? WHERE id = ?'

        cursor.execute(query, list(kwargs.values()) + [timestamp, id])
        self.conn.commit()
        return True

    def delete_password(self, id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM passwords WHERE id = ?', (id,))
        self.conn.commit()
        return True

    def reset_database(self) -> bool:
        """Clear all data from tables without dropping them."""
        try:
            cursor = self.conn.cursor()
            # Delete all records instead of dropping tables
            cursor.execute('DELETE FROM passwords')
            cursor.execute('DELETE FROM categories')
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error resetting database: {e}")
            return False

    @lru_cache(maxsize=32)
    def get_all_categories(self) -> tuple:
        cursor = self.conn.cursor()
        cursor.execute('SELECT name FROM categories ORDER BY name')
        return tuple(row[0] for row in cursor.fetchall())

    def clear_category_cache(self):
        """Manually clear the category cache."""
        self.get_all_categories.cache_clear()

    def add_category(self, category: str) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO categories (name) VALUES (?)', (category,))
            self.conn.commit()
            self.clear_category_cache() # Clear cache after adding category
            return True
        except sqlite3.IntegrityError:
            # Category already exists
            return False

    def delete_category(self, category: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM categories WHERE name = ?', (category,))
        self.conn.commit()
        self.clear_category_cache() # Clear cache after deleting category
        return True