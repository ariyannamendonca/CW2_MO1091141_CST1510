import sqlite3
import os
from pathlib import Path

DB_PATH = Path("DATA") / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    """Connect to SQLite database, create file if it doesn't exist"""
    return sqlite3.connect(str(db_path))

def delete_database(db_path=DB_PATH):
    """Deletes database"""
    db_path = Path(db_path)

    if db_path.exists():
        os.remove(db_path)
        print(f"Database deleted {db_path}")

def create_users_table(conn):
    """Create users table if it doesn't exist"""
    cursor = conn.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    cursor.execute(create_table_sql)
    conn.commit()
    print(f"Users table created {create_table_sql}")

def create_cyber_incidents_table(conn):
    """creates cyber incidents table"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT DEFAULT 'open',
                    date TEXT,
                    reported_by_user TEXT,
                    FOREIGN KEY (reported_by_username) REFERENCES users(username)
        )
    """)
    conn.commit()
    print("Cyber incidents table created.")