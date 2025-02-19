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
        cursor.execute('DROP TABLE IF EXISTS device_languages')
        cursor.execute('''
            CREATE TABLE device_languages (
                device_id TEXT PRIMARY KEY,
                language TEXT DEFAULT 'english'
            )
        ''')
        
        self.conn.commit()

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