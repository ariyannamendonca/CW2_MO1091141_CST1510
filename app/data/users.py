from app.data.db import connect_database

class Users:
    """does CRUD functions users"""

    def __init__(self, conn):
        self.conn = conn

    def get_user_by_username(self,username):
        """Retrieve user by username"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()
        return user

    def insert_user(self,username, password_hash, role='user'):
        """Insert new user"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_user(self, username, new_role):
        """Update user role"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE users
            SET role = ?
            WHERE username = ?
            """, (new_role, username))
        self.conn.commit()
        return cursor.rowcount

    def delete_user(self, username):
        """Delete user"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        self.conn.commit()
        return cursor.rowcount