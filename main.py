from app.data.db import connect_database, delete_database
from app.data.schema import create_all_tables
from app.services.user_service import register_user, login_user, migrate_users_from_file, load_csv_to_table, DATASETS_CSV, IT_TICKETS_CSV, CYBER_INCIDENTS_CSV
from app.data.incidents import insert_incident, get_all_incidents, update_incident_status, delete_incident_status

def main():
    print("=" * 60)
    print("Week 8: Database Demo")
    print("=" * 60)

    # 1. Setup database
    delete_database()

    conn = connect_database()
    create_all_tables(conn)

    # 2. Migrate users
    migrate_users_from_file(conn)

    # 3. move csv data
    print("Moving CSV data")
    load_csv_to_table(conn, DATASETS_CSV, "datasets_metadata")
    load_csv_to_table(conn, IT_TICKETS_CSV, "it_tickets")
    load_csv_to_table(conn, CYBER_INCIDENTS_CSV, "cyber_incidents")

    # 4. Test authentication
    success, msg = register_user("alice", "SecurePass123!", "analyst")
    print(msg)

    success, msg = login_user("alice", "SecurePass123!")
    print(msg)

    # 5. Test CRUD
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

if __name__ == "__main__":
    main()
    verify_user_migration()
