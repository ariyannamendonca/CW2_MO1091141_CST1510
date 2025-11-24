import sqlite3
from pathlib import Path

DB_PATH = Path("Data") / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    """Connect to SQLite database"""
    return sqlite3.connect(str(db_path))
