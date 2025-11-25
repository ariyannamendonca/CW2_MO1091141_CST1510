from app.data.db import connect_database, delete_database
from app.data.schema import create_all_tables
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import insert_incident, get_all_incidents

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

    # 3. Test authentication
    success, msg = register_user("charlie", "charliepass123!", "analyst")
    print(msg)

    success, msg = login_user("bob", "bob123456789")
    print(msg)

    # 4. Test CRUD
    incident_id = insert_incident(
        "2024-11-05",
        "Phishing",
        "High",
        "Open",
        "Suspicious email detected",
        "bob"
    )
    print(f"Created incident #{incident_id}")

    # 5. Query data
    df = get_all_incidents()
    print(f"Total incidents: {len(df)}")

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
