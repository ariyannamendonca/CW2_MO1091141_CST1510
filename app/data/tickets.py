import pandas as pd
from app.data.db import connect_database

class ITickets:
    """does CRUD functions and analytical queries for IT tickets"""

    def __init__(self, conn):
        self.conn = conn

    def insert_ticket(self, ticket_id, priority, status, category, subject, description, created_date, resolved_date, resolution_time_hours, assigned_to):
        """Inserts ticket into database."""
        cursor = self.conn.cursor()
        sql_insert = """
            INSERT INTO it_tickets
            (ticket_id, priority, status, category, subject, description, created_date, resolved_date, resolution_time_hours, assigned_to)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        values = (ticket_id, priority, status, category, subject, description, created_date, resolved_date, resolution_time_hours, assigned_to)
        cursor.execute(sql_insert, values)
        self.conn.commit()
        return cursor.lastrowid

    def get_tickets(self):
        """Gets tickets from database as a df."""
        df = pd.read_sql_query(
            "SELECT * FROM it_tickets ORDER BY id DESC",
            self.conn
        )
        return df

    def update_tickets(self, ticket_id, status):
        """Updates tickets in database."""
        cursor = self.conn.cursor()
        sql_update = """
            UPDATE it_tickets
            SET status = ?
            WHERE ticket_id = ?
        """

        cursor.execute(sql_update, (status, ticket_id))
        self.conn.commit()
        return cursor.rowcount

    def delete_ticket(self, ticket_id):
        """Deletes ticket from database."""
        cursor = self.conn.cursor()
        sql_delete = """
            DELETE FROM it_tickets
            WHERE ticket_id = ?
        """
        cursor.execute(sql_delete, (ticket_id,))
        self.conn.commit()
        return cursor.rowcount

    #analytical queries
    def get_tickets_by_status_count(self):
        """Gets tickets by status """
        query = """
            SELECT status, COUNT(*) as count
            FROM it_tickets
            GROUP BY status
            ORDER BY count DESC
        """
        df = pd.read_sql_query(query, self.conn)
        return df

    def get_high_severity_by_priority(self):
        """Count high severity by priority"""
        query = """
            SELECT priority, COUNT(*) as count
            FROM it_tickets
            WHERE priority = 'High'
            GROUP BY priority
            ORDER BY count DESC
        """
        df = pd.read_sql_query(query, self.conn)
        return df

    def get_assigned_to_with_many_cases(self, min_count=5):
        """gets assigned to tickets"""
        query = """
            SELECT assigned_to, COUNT(*) as count
            FROM it_tickets
            GROUP BY assigned_to
            HAVING COUNT(*) > ?
            ORDER BY count DESC
        """
        df = pd.read_sql_query(query, self.conn, params=(min_count,))
        return df
