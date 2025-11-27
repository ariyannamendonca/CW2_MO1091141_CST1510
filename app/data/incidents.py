import pandas as pd
from app.data.db import connect_database

def insert_incident(conn, date, category, severity, status, description, reported_by=None):
    """Insert new cyber incident."""
    cursor = conn.cursor()

    sql_insert = """
        INSERT INTO cyber_incidents
        (timestamp, category, severity, status, description, reported_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(sql_insert, (date, category, severity, status, description, reported_by))

    conn.commit()
    return cursor.lastrowid

def get_all_incidents(conn):
    """Get all incidents."""
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents ORDER BY incident_id DESC",
        conn
    )
    return df

def update_incident_status(conn, incident_id, status):
    """Update incident status."""
    cursor = conn.cursor()
    sql_update = """
        UPDATE cyber_incidents
        SET status = ?
        WHERE incident_id = ?
    """
    cursor.execute(sql_update, (status, incident_id))
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

#Analytical queries (the big 6)
def get_incidents_by_type_count(conn):
    """Count incidents by type."""
    query = """
    SELECT category, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY category
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_high_severity_by_status(conn):
    """Get high severity by status."""
    query = """
    SELECT status, COUNT(*) as count
    FROM cyber_incidents
    WHERE severity = 'High'
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_incidents_type_with_many_cases(conn, min_count=5):
    """Get incidents by type."""
    query = """
    SELECT category, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY category
    HAVING COUNT(*) > ?
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn, params=(min_count,))
    return df
