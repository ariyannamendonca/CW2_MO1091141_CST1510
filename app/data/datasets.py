import pandas as pd
from app.data.db import connect_database

def insert_dataset(conn, name, category, uploaded_by, upload_date, rows, columns, file_size_mb, created_at):
    """Insert new dataset."""
    cursor = conn.cursor()

    sql_insert = """
        INSERT INTO datasets_metadata
        (name, category, uploaded_by, upload_date, rows, columns, file_size_mb, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(sql_insert, (name, category, uploaded_by, upload_date, rows, columns, file_size_mb, created_at))

    conn.commit()
    return cursor.lastrowid

def get_all_datasets(conn):
    """Gets all dataset metadata as a df."""
    df = pd.read_sql_query(
        "SELECT * FROM datasets_metadata ORDER BY dataset_id DESC",
        conn
    )
    return df

def update_dataset_category(conn, dataset_id, category):
    """Updates dataset category."""
    cursor = conn.cursor()
    sql_update = """
        UPDATE datasets_metadata
        SET category = ?
        WHERE dataset_id = ?
    """
    cursor.execute(sql_update, (category, dataset_id))
    conn.commit()
    return cursor.rowcount

def delete_dataset(conn, dataset_id):
    """Deletes dataset."""
    cursor = conn.cursor()
    sql_delete = """
        DELETE FROM datasets_metadata
        WHERE dataset_id = ?
    """

    cursor.execute(sql_delete, (dataset_id,))
    conn.commit()
    return cursor.rowcount

#Analytical queries (the big 6)
def get_dataset_by_uploader(conn, min_rows=1000):
    """counts datasets by their uploader if they have more than min_rows"""
    query="""
    SELECT uploaded_by, COUNT(*) as count
    FROM datasets_metadata
    WHERE rows > ?
    GROUP BY uploaded_by
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn, params=(min_rows,))
    return df
