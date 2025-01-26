import sqlite3
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path='chat_database.db'):
        """Initialize database connection"""
        os.makedirs('chat_backups', exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.setup_database()

    def setup_database(self):
        cursor = self.conn.cursor()
        
        # Drop existing tables if needed
        cursor.execute('DROP TABLE IF EXISTS messages')
        cursor.execute('DROP TABLE IF EXISTS device_languages')
        
        # Create messages table with language column
        cursor.execute('''
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY,
                sender TEXT,
                receiver TEXT,
                message TEXT,
                timestamp TEXT,
                language TEXT DEFAULT 'english'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE device_languages (
                device_id TEXT PRIMARY KEY,
                language TEXT DEFAULT 'english'
            )
        ''')
        
        self.conn.commit()

    def save_message(self, sender, receiver, message, language='english'):
        """Save message to database with language"""
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO messages 
            (sender, receiver, message, timestamp, language) 
            VALUES (?, ?, ?, ?, ?)
        ''', (sender, receiver, message, timestamp, language))
        self.conn.commit()

    def get_chat_history(self, sender, receiver):
        """Retrieve chat history between two devices"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT sender, message, timestamp, language 
            FROM messages 
            WHERE (sender = ? AND receiver = ?) OR 
                  (sender = ? AND receiver = ?)
            ORDER BY timestamp
        ''', (sender, receiver, receiver, sender))
        return cursor.fetchall()

    def save_device_language(self, device_id, language):
        """Save or update device's language preference"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO device_languages 
            (device_id, language) VALUES (?, ?)
        ''', (device_id, language))
        self.conn.commit()

    def get_device_language(self, device_id):
        """Retrieve device's language preference"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT language FROM device_languages 
            WHERE device_id = ?
        ''', (device_id,))
        result = cursor.fetchone()
        return result[0] if result else 'english'

    def close(self):
        """Close database connection"""
        self.conn.close()