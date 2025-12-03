import pandas as pd

from app.data.db import PROJECT_ROOT, connect_database, DB_PATH
from app.data.schema import create_all_tables
from app.services.user_service import migrate_users_from_file


def csv_path(filename):
    return PROJECT_ROOT / "DATA" / filename

def load_cyber_incidents(conn):
    """Load cyber_incidents.csv in database"""
    try:
        df = pd.read_csv(csv_path("cyber_incidents.csv"))

        if "incident_id" in df.columns:
            df = df.drop(columns=["incident_id"])

        df.to_sql("cyber_incidents", conn, if_exists="append", index=False)
        print(f" Successfully loaded {len(df)} rows into 'cyber_incidents'")
        return len(df)

    except Exception as e:
        print(f"Error loading data into 'cyber_incidents' table: {e}")
        return 0

def load_datasets_metadata(conn):
    """Load datasets_metadata.csv in database"""
    try:
        df = pd.read_csv(csv_path("datasets_metadata.csv"))

        if "dataset_id" in df.columns:
            df = df.drop(columns=["dataset_id"])

        df.to_sql("datasets_metadata", conn, if_exists="append", index=False)
        print(f" Successfully loaded {len(df)} rows into 'datasets_metadata'")
        return len(df)

    except Exception as e:
        print(f"Error loading data into 'datasets_metadata' table: {e}")
        return 0

def load_it_tickets(conn):
    """Load it_tickets.csv in database"""
    try:
        df = pd.read_csv(csv_path("it_tickets.csv"))

        if "id" in df.columns:
            df = df.drop(columns=["id"])

        if "ticket_id" in df.columns:
            df = df.drop(columns=["ticket_id"])

        df.to_sql("it_tickets", conn, if_exists="append", index=False)
        print(f" Successfully loaded {len(df)} rows into 'it_tickets'")
        return len(df)

    except Exception as e:
        print(f"Error loading data into 'it_tickets' table: {e}")
        return 0

def load_all_csv_data(conn):
    """Load all_csv_data.csv in database"""
    print("Moving all CSV data")

    total = 0
    total += load_cyber_incidents(conn)
    total += load_datasets_metadata(conn)
    total += load_it_tickets(conn)

    return total

def setup_database_complete():
    """
    Complete database setup:
    1. Connect to database
    2. Create all tables
    3. Migrate users from users.txt
    4. Load CSV data for all domains
    5. Verify setup
    """
    print("\n" + "=" * 60)
    print("STARTING COMPLETE DATABASE SETUP")
    print("=" * 60)

    # Step 1: Connect
    print("\n[1/5] Connecting to database...")
    conn = connect_database()
    print("       Connected")

    # Step 2: Create tables
    print("\n[2/5] Creating database tables...")
    create_all_tables(conn)

    # Step 3: Migrate users
    print("\n[3/5] Migrating users from users.txt...")
    user_count = migrate_users_from_file(conn)
    print(f"       Migrated {user_count} users")

    # Step 4: Load CSV data
    print("\n[4/5] Loading CSV data...")
    total_rows = load_all_csv_data(conn)

    # Step 5: Verify
    print("\n[5/5] Verifying database setup...")
    cursor = conn.cursor()

    # Count rows in each table
    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
    print("\n Database Summary:")
    print(f"{'Table':<25} {'Row Count':<15}")
    print("-" * 40)

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:<25} {count:<15}")

    conn.close()

    print("\n" + "=" * 60)
    print(" DATABASE SETUP COMPLETE!")
    print("=" * 60)
    print(f"\n Database location: {DB_PATH.resolve()}")
    print("\nYou're ready for Week 9 (Streamlit web interface)!")

# Run the complete setup
setup_database_complete()