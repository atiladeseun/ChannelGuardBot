import sqlite3
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
DB_PATH = "channelguard.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TEXT,
            trial_until TEXT,
            is_paid INTEGER DEFAULT 0
        )''')
        
        # Channels table
        c.execute('''CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            channel_id INTEGER,
            channel_title TEXT,
            added_at TEXT
        )''')
        
        # Joins table
        c.execute('''CREATE TABLE IF NOT EXISTS joins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER,
            user_id INTEGER,
            username TEXT,
            first_name TEXT,
            joined_at TEXT
        )''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def add_user(user_id, username, first_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        trial_until = (datetime.now() + timedelta(days=FREE_TRIAL_DAYS)).isoformat()
        c.execute("INSERT OR REPLACE INTO users (user_id, username, first_name, joined_at, trial_until) VALUES (?,?,?,?,?)",
                  (user_id, username or "", first_name or "", datetime.now().isoformat(), trial_until))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error adding user {user_id}: {e}")

def get_user(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        return row
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return None

def add_channel(user_id, channel_id, channel_title):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO channels (user_id, channel_id, channel_title, added_at) VALUES (?,?,?,?)",
                  (user_id, channel_id, channel_title or "Unknown", datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error adding channel: {e}")

def get_channels(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM channels WHERE user_id = ?", (user_id,))
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Error getting channels for user {user_id}: {e}")
        return []

def log_join(channel_id, user_id, username, first_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO joins (channel_id, user_id, username, first_name, joined_at) VALUES (?,?,?,?,?)",
                  (channel_id, user_id, username or "", first_name or "", datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error logging join: {e}")

def get_today_joins(channel_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        today = datetime.now().date().isoformat()
        c.execute("SELECT * FROM joins WHERE channel_id = ? AND DATE(joined_at) = ?", (channel_id, today))
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Error getting today's joins: {e}")
        return []
