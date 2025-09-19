import sqlite3
from sqlite3 import Connection
from datetime import datetime
from typing import List, Dict, Optional

import os

DB_PATH = "data/chat_data.db"

# Ensure the data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_connection() -> Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        user_type TEXT NOT NULL,
        user_input TEXT NOT NULL,
        intent TEXT NOT NULL,
        bot_reply TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        income INTEGER NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        category TEXT NOT NULL,
        amount INTEGER NOT NULL,
        FOREIGN KEY (user_name) REFERENCES users(name)
    )
    """)
    conn.commit()
    conn.close()

def insert_chat_log(user_name: str, user_type: str, user_input: str, intent: str, bot_reply: str):
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.utcnow().isoformat()
    cursor.execute("""
    INSERT INTO chat_logs (user_name, user_type, user_input, intent, bot_reply, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_name, user_type, user_input, intent, bot_reply, timestamp))
    conn.commit()
    conn.close()

def fetch_chat_logs(limit: Optional[int] = 100) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT user_name, user_type, user_input, intent, bot_reply, timestamp
    FROM chat_logs
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    logs = []
    for row in rows:
        logs.append({
            "user_name": row[0],
            "user_type": row[1],
            "user_input": row[2],
            "intent": row[3],
            "bot_reply": row[4],
            "timestamp": row[5]
        })
    return logs

def save_user(name: str, type: str, income: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (name, type, income) VALUES (?, ?, ?)", (name, type, income))
    conn.commit()
    conn.close()

def save_expenses(user_name: str, expenses_dict: Dict[str, int]):
    conn = get_connection()
    cursor = conn.cursor()
    # Delete old expenses for user
    cursor.execute("DELETE FROM expenses WHERE user_name = ?", (user_name,))
    for cat, amt in expenses_dict.items():
        cursor.execute("INSERT INTO expenses (user_name, category, amount) VALUES (?, ?, ?)", (user_name, cat, amt))
    conn.commit()
    conn.close()

def load_user(name: str) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT type, income FROM users WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"type": row[0], "income": row[1]}
    return None

def load_expenses(user_name: str) -> Dict[str, int]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, amount FROM expenses WHERE user_name = ?", (user_name,))
    rows = cursor.fetchall()
    conn.close()
    expenses = {}
    for cat, amt in rows:
        expenses[cat] = amt
    return expenses
