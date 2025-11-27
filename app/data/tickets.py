import pandas as pd
from app.data.db import connect_database

def insert_ticket(conn, ticket_id, priority, status, category, subject, description, created_date, resolved_date, resolution_time_hours, assigned_to):
    """Inserts ticket into database."""
    cursor = conn.cursor()
    sql_insert = """
        INSERT INTO it_tickets
        (ticket_id, priority, status, category, subject, description, created_date, resolved_date, resolution_time_hours, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = (ticket_id, priority, status, category, subject, description, created_date, resolved_date, resolution_time_hours, assigned_to)
    cursor.execute(sql_insert, values)
    conn.commit()
    return cursor.lastrowid

def get_tickets(conn):
    """Gets tickets from database as df."""
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets ORDER BY id DESC",
        conn
    )
    return df

def update_tickets(conn, ticket_id, assigned_to, status):
    """Updates tickets in database."""
    cursor = conn.cursor()
    sql_update = """
        UPDATE it_tickets
        SET assigned_to = ?,, status = ?
        WHERE ticket_id = ?
    """

    cursor.execute(sql_update, (assigned_to, status, ticket_id))
    conn.commit()
    return cursor.rowcount

def delete_ticket(conn, ticket_id):
    """Deletes ticket from database."""
    cursor = conn.cursor()
    sql_delete = """
        DELETE FROM it_tickets
        WHERE ticket_id = ?
    """
    cursor.execute(sql_delete, (ticket_id,))
    conn.commit()
    return cursor.rowcount

def get_tickets_by_status_count(conn):
    """Gets tickets by status """
    query = """
    SELECT status, COUNT(*) as count
    FROM it_tickets
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_high_severity_by_priority(conn):
    """Count high severity by priority"""
    query = """
    SELECT priority, COUNT(*) as count
    FROM it_tickets
    WHERE priority = 'High'
    GROUP BY priority
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_assigned_to_with_many_cases(conn, min_count=5):
    """gets assigned to tickets"""
    query = """
    SELECT assigned_to, COUNT(*) as count
    FROM it_tickets
    GROUP BY assigned_to
    HAVING COUNT(*) > ?
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn, params=(min_count,))
    return df
