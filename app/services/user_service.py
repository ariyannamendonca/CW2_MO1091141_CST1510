import sqlite3
from pathlib import Path

import bcrypt
import pandas as pd

from app.data.db import connect_database

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "DATA"

USER_FILEPATH = DATA_DIR / "user.txt"
DATASETS_CSV = DATA_DIR / "datasets_metadata.csv"
IT_TICKETS_CSV = DATA_DIR / "it_tickets.csv"
CYBER_INCIDENTS_CSV = DATA_DIR / "cyber_incidents.csv"

class Userservice:
    """Does migration of user information and CSV data into database"""

    def __init__(self, conn):
        self.conn = conn

    def register_user(self,username, password, role='user'):
        """Register a new user in database."""
        cursor = self.conn.cursor()

        #checks if user already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, f"User '{username}' already exists."

        #hash password
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        password_hash = hashed.decode('utf-8')

        #insert new user
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role)
        )
        self.conn.commit()
        return True, f"User '{username}' registered successfully."

    def login_user(self, username, password):
        """Authenticate user in database."""
        cursor = self.conn.cursor()

        #finds user
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user:
            return False, "User not found."

        #verify password
        stored_hash = user[2] #password_hash column
        password_bytes = password.encode('utf-8')
        hash_bytes = stored_hash.encode('utf-8')

        if bcrypt.checkpw(password_bytes, hash_bytes):
            return True, f"Welcome {username}!"
        else:
            return False, "Invalid password."

    def migrate_users_from_file(self, filepath = USER_FILEPATH):
        """Migrate users from text file to database (users)."""
        if not filepath.exists():
            print(f"File not found: {filepath}")
            print("     No users to migrate.")
            return 0

        cursor = self.conn.cursor()
        migrated_count = 0

        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split(',')
                if len(parts) >= 2:
                    username = parts[0]
                    password_hash = parts[1]

                    #Insert user
                    try:
                        cursor.execute(
                            "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                            (username, password_hash, 'user')
                        )
                        if cursor.rowcount > 0:
                            migrated_count += 1
                    except sqlite3.Error as e:
                        print(f"Error migrating user{username}: {e}")

        self.conn.commit()
        return migrated_count

    def load_csv_to_table(self, csv_path, table_name):
        """Load csv into table"""
        if not csv_path.exists():
            print(f"File not found: {csv_path}")
            return 0

        try:
            df = pd.read_csv(csv_path)
            rows_to_load = len(df)

            # Use df.to_sql() to insert data
            df.to_sql(
                name=table_name,
                con=self.conn,
                if_exists='append',
                index=False # Do not save the DataFrame index as a column
            )
            self.conn.commit()

            print(f" Successfully loaded {rows_to_load} rows into '{table_name}' from {csv_path.name}")
            return rows_to_load

        except Exception as e:
            print(f"Error loading data from {csv_path.name} into {table_name}: {e}")
            return 0
