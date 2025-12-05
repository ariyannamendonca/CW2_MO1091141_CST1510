import sqlite3
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "DATA" / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    """Connect to SQLite database"""
    return sqlite3.connect(str(db_path)) #automatically creates file if it doesn't exist, connection made

def delete_database(db_path=DB_PATH):
    """Deletes database"""
    db_path = Path(db_path)

    if db_path.exists():
        os.remove(db_path) #file deletion
        print(f"Database deleted {db_path}")