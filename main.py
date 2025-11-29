from app.data.datasets import get_dataset_by_uploader
from app.data.db import connect_database, delete_database
from app.data.schema import create_all_tables
from app.data.tickets import get_assigned_to_with_many_cases, get_tickets_by_status_count
from app.services.user_service import register_user, login_user, migrate_users_from_file, load_csv_to_table, DATASETS_CSV, IT_TICKETS_CSV, CYBER_INCIDENTS_CSV
from app.data.incidents import insert_incident, get_all_incidents, update_incident_status, delete_incident_status, \
    get_incidents_by_type_count, get_high_severity_by_status


def setup_database():
    print("=" * 60)
    print("Week 8: Database Demo")
    print("=" * 60)

    # 1. delete database
    delete_database()

    db_conn = connect_database()
    create_all_tables(db_conn)

    # 2. Migrate users
    migrate_users_from_file(db_conn)

    # 3. move csv data
    print("Moving CSV data")
    load_csv_to_table(db_conn, DATASETS_CSV, "datasets_metadata")
    load_csv_to_table(db_conn, IT_TICKETS_CSV, "it_tickets")
    load_csv_to_table(db_conn, CYBER_INCIDENTS_CSV, "cyber_incidents")

    #verify table exists
    cursor = db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:", tables)

    db_conn.close()

    # 4. Test authentication
def test_user_auth():
    print("\n TESTING USER AUTHENTICATION")
    conn = connect_database()
    success, msg = register_user("alice", "SecurePass123!", "analyst")
    print(msg)
    success, msg = login_user("alice", "SecurePass123!")
    print(msg)
    conn.close()

    # 5. Test CRUD
def test_incident_crud():
    print("\n TESTING INCIDENT CRUD")
    conn = connect_database()

    incident_id = insert_incident(conn,
        "2024-11-05",
        "Phishing",
        "High",
        "Open",
        "Suspicious email detected",
        "alice"
    )
    print(f"Created incident #{incident_id}")

    df = get_all_incidents(conn)
    print(f"Total incidents before update: {len(df)}")

    rows_updated = update_incident_status(conn, incident_id,"In Progress")
    print(f"Updated status for incident #{incident_id}. Rows modified {rows_updated}")

    df = get_all_incidents(conn)
    print(f"Total incidents after update: {len(df)}")

    rows_deleted = delete_incident_status (conn, incident_id)
    print(f"Deleted incidents #{incident_id}. Rows deleted {rows_deleted}")

    df = get_all_incidents(conn)
    print(f"Total incidents after delete: {len(df)}")

    conn.close()

def verify_user_migration():
    """verify users were migrated"""
    print("\n" + "=" * 35)
    print("MIGRATION VERIFICATION")
    print("=" * 35)

    conn = connect_database()
    cursor = conn.cursor()

    #query all users
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()

    print("Users in database:")
    print(f"{'ID':<5} {'Username':<15} {'Role':<10}")
    print("-" * 35)
    for user in users:
        print(f"{user[0]:<5} {user[1]:<15} {user[2]:<10}")

    print(f"\nTotal users: {len(users)}")
    conn.close()

def run_analytical_queries():
    #analytical queries for cyber incidents
    conn = connect_database()

    print("\n Incidents by Type:")
    df_by_type = get_incidents_by_type_count(conn)
    print(df_by_type)

    print("\n High Severity Incidents by Status:")
    df_high_severity = get_high_severity_by_status(conn)
    print(df_high_severity)

    print("\n Incident Types with Many Cases (>5):")
    df_many_cases = get_assigned_to_with_many_cases(conn)
    print(df_many_cases)

    conn.close()

    #analytical queries for IT tickets
    conn = connect_database()

    print("\n Tickets by Status:")
    df_by_status = get_tickets_by_status_count(conn)
    print(df_by_status)

    print("\n High severity by Priority:")
    df_high_severity = get_high_severity_by_status(conn)
    print(df_high_severity)

    print("\n Assigned cases:")
    df_many_cases = get_assigned_to_with_many_cases(conn)
    print(df_many_cases)

    conn.close()

    #analytical queries for datasets metadata
    conn = connect_database()

    print("\n Large datasets by uploader:")
    df_large_datasets = get_dataset_by_uploader(conn)
    print(df_large_datasets)

    conn.close()

if __name__ == "__main__":
    setup_database()
    verify_user_migration()
    test_user_auth()
    test_incident_crud()
    run_analytical_queries()