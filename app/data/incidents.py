import pandas as pd
from app.data.db import connect_database

def insert_incident(conn, date, incident_type, severity, status, description, reported_by=None):
    """Insert new cyber incident."""
    cursor = conn.cursor()

    sql_insert = """
        INSERT INTO cyber_incidents
        (timestamp, category, severity, status, description, reported_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(sql_insert, (date, incident_type, severity, status, description, reported_by))

    conn.commit()
    return cursor.lastrowid

def get_all_incidents(conn):
    """Get all incidents as DataFrame."""
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents ORDER BY incident_id DESC",
        conn
    )
    return df

def update_incident_status(conn, incident_id, new_status):
    """Update incident status."""
    cursor = conn.cursor()
    sql_update = """
        UPDATE cyber_incidents
        SET status = ?
        WHERE incident_id = ?
    """
    cursor.execute(sql_update, (new_status, incident_id))
    conn.commit()
    return cursor.rowcount

def delete_incident_status(conn, incident_id):
    """Delete incident status."""
    cursor = conn.cursor()
    sql_delete = """
        DELETE FROM cyber_incidents
        WHERE incident_id = ?
    """
    cursor.execute(sql_delete, (incident_id,))
    conn.commit()
    return cursor.rowcount
