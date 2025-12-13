import pandas as pd
from app.data.db import connect_database

class Datasets:
    """does CRUD functions and analytical queries for datasets metadata"""

    def __init__(self, conn):
        self.conn = conn

    def insert_dataset(self, name, category, uploaded_by, upload_date, rows, columns, file_size_mb, created_at):
        """Insert new dataset."""
        cursor = self.conn.cursor()
        sql_insert = """
            INSERT INTO datasets_metadata
            (name, category, uploaded_by, upload_date, rows, columns, file_size_mb, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql_insert, (name, category, uploaded_by, upload_date, rows, columns, file_size_mb, created_at))
        self.conn.commit()
        return cursor.lastrowid

    def get_all_datasets(self):
        """Gets all dataset metadata as a df."""
        df = pd.read_sql_query(
            "SELECT * FROM datasets_metadata ORDER BY dataset_id DESC",
            self.conn
        )
        return df

    def update_dataset_category(self, dataset_id, category):
        """Updates dataset category."""
        cursor = self.conn.cursor()
        sql_update = """
            UPDATE datasets_metadata
            SET category = ?
            WHERE dataset_id = ?
        """
        cursor.execute(sql_update, (category, dataset_id))
        self.conn.commit()
        return cursor.rowcount

    def update_dataset_rows_columns(self, dataset_id, rows, columns):
        """Updates dataset rows and columns."""
        sql = """
            UPDATE datasets_metadata
            SET rows = ?, 
            columns = ?
            WHERE dataset_id = ?;
        """
        params = (int(rows), int(columns), int(dataset_id))
        rows_affected = 0
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            self.conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()

        except Exception as e:
            print(f"Database error during update: {e}")

        return rows_affected

    def delete_dataset(self, dataset_id):
        """Deletes dataset."""
        cursor = self.conn.cursor()
        sql_delete = """
                DELETE FROM datasets_metadata
                WHERE dataset_id = ?
        """

        cursor.execute(sql_delete, (dataset_id,))
        self.conn.commit()
        return cursor.rowcount

    #Analytical queries (the big 6)
    def get_dataset_by_uploader(self, min_rows=1000):
        """counts datasets by their uploader if they have more than min_rows"""
        query="""
            SELECT uploaded_by, COUNT(*) as count
            FROM datasets_metadata
            WHERE rows > ?
            GROUP BY uploaded_by
            ORDER BY count DESC
        """
        df = pd.read_sql_query(query, self.conn, params=(min_rows,))
        return df