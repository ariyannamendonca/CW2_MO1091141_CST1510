import sqlite3
import os
from pathlib import Path

DB_PATH = Path("DATA") / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    """Connect to SQLite database"""
    return sqlite3.connect(str(db_path))

def delete_database(db_path=DB_PATH):
    """Deletes database"""
    db_path = Path(db_path)

    if db_path.exists():
        os.remove(db_path)
        print(f"Database deleted {db_path}")
