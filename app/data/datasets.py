import pandas as pd
from app.data.db import connect_database

def insert_dataset(conn, dataset_id, name, category, uploaded_by, upload_date,columns, file_size_mb, created_at):
    """Insert new dataset."""
    cursor = conn.cursor()

    sql_insert = """
        INSERT INTO datasets_metadata
        (dataset_id, name, category, uploaded_by, upload_date, columns, file_size_mb, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(sql_insert, (dataset_id, name, category, uploaded_by, upload_date, columns, file_size_mb, created_at))

    conn.commit()
    return cursor.rowcount

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
