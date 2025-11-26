import bcrypt
import pandas as pd
import sqlite3
from pathlib import Path
from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user

DATA_DIR = Path("DATA")
USER_FILEPATH = Path("DATA") / "user.txt"
DATASETS_CSV = DATA_DIR / "datasets_metadata.csv"
IT_TICKETS_CSV = DATA_DIR / "it_tickets.csv"
CYBER_INCIDENTS_CSV = DATA_DIR / "cyber_incidents.csv"
def register_user(username, password, role='user'):
    """Register a new user in database."""
    conn = connect_database()
    cursor = conn.cursor()

    #checks if user already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
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
    conn.commit()
    conn.close()

    return True, f"User '{username}' registered successfully."

def login_user(username, password):
    """Authenticate user in database."""
    conn = connect_database()
    cursor = conn.cursor()

    #find user
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

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

def migrate_users_from_file(conn, filepath = USER_FILEPATH):
    """Migrate users from text file to database(users)."""
    #...migration Logic
    if not filepath.exists():
        print(f"File not found: {filepath}")
        print("     No users to migrate.")
        return

    cursor = conn.cursor()
    migrated_count = 0

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            #Parse line: username,password_hash
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

def load_csv_to_table(conn, csv_path, table_name):
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
            con=conn,
            if_exists='append',
            index=False # Do not save the DataFrame index as a column
        )

        print(f" Successfully loaded {rows_to_load} rows into '{table_name}' from {csv_path.name}")
        return rows_to_load

    except Exception as e:
        print(f"Error loading data from {csv_path.name} into {table_name}: {e}")
        return 0

    conn.commit()
    print(f"Migrated {migrated_count} user from {filepath.name}")

