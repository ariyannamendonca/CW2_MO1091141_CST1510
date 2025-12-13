import pandas as pd
from app.data.db import connect_database

class Cyberincidents:
    """does CRUD functions and analytical queries for cyber incidents"""

    def __init__(self, conn):
        self.conn = conn

    def insert_incident(self, date, category, severity, status, description, reported_by=None):
        """Insert new cyber incident."""
        cursor = self.conn.cursor()
        sql_insert = """
            INSERT INTO cyber_incidents
            (timestamp, category, severity, status, description, reported_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql_insert, (date, category, severity, status, description, reported_by))
        self.conn.commit()
        return cursor.lastrowid

    def get_all_incidents(self):
        """Gets all incidents."""
        df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents ORDER BY incident_id DESC",
            self.conn
        )
        return df

    def update_incident_status(self, incident_id, status):
        """Update the status of incidents."""
        cursor = self.conn.cursor()
        sql_update = """
            UPDATE cyber_incidents
            SET status = ?
            WHERE incident_id = ?
        """
        cursor.execute(sql_update, (status, incident_id))
        self.conn.commit()
        return cursor.rowcount

    def delete_incident_status(self, incident_id):
        """Deletes incidents."""
        cursor = self.conn.cursor()
        sql_delete = """
            DELETE FROM cyber_incidents
            WHERE incident_id = ?
        """
        cursor.execute(sql_delete, (incident_id,))
        self.conn.commit()
        return cursor.rowcount

    def get_incident_by_id(self, incident_id):
        """Get an incident by its id."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM cyber_incidents WHERE incident_id = ?", (incident_id,))
        return cursor.fetchone()

    #Analytical queries (the big 6)
    def get_incidents_by_type_count(self):
        """Count incidents by type."""
        query = """
            SELECT category, COUNT(*) as count
            FROM cyber_incidents
            GROUP BY category
            ORDER BY count DESC
        """
        df = pd.read_sql_query(query, self.conn)
        return df

    def get_high_severity_by_status(self):
        """Get high severity by status."""
        query = """
            SELECT status, COUNT(*) as count
            FROM cyber_incidents
            WHERE severity = 'High'
            GROUP BY status
            ORDER BY count DESC
        """
        df = pd.read_sql_query(query, self.conn)
        return df

    def get_incidents_type_with_many_cases(self, min_count=5):
        """Get incidents by type."""
        query = """
            SELECT category, COUNT(*) as count
            FROM cyber_incidents
            GROUP BY category
            HAVING COUNT(*) > ?
            ORDER BY count DESC
        """
        df = pd.read_sql_query(query, self.conn, params=(min_count,))
        return df
