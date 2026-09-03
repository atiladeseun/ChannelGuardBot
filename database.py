import sqlite3
from datetime import datetime, timedelta

DB_PATH = "channelguard.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        joined_at TEXT,
        trial_until TEXT,
        is_paid BOOLEAN DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        channel_id INTEGER,
        channel_title TEXT,
        added_at TEXT
    )''')
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

def add_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    trial_until = (datetime.now() + timedelta(days=FREE_TRIAL_DAYS)).isoformat()
    c.execute("INSERT OR REPLACE INTO users (user_id, username, first_name, joined_at, trial_until) VALUES (?,?,?,?,?)",
              (user_id, username, first_name, datetime.now().isoformat(), trial_until))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def add_channel(user_id, channel_id, channel_title):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO channels (user_id, channel_id, channel_title, added_at) VALUES (?,?,?,?)",
              (user_id, channel_id, channel_title, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_channels(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM channels WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def log_join(channel_id, user_id, username, first_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO joins (channel_id, user_id, username, first_name, joined_at) VALUES (?,?,?,?,?)",
              (channel_id, user_id, username, first_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_today_joins(channel_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today = datetime.now().date().isoformat()
    c.execute("SELECT * FROM joins WHERE channel_id = ? AND DATE(joined_at) = ?", (channel_id, today))
    rows = c.fetchall()
    conn.close()
    return rows
