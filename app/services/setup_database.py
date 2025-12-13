from app.data.db import connect_database, delete_database
from app.data.schema import create_all_tables

from app.data.incidents import Cyberincidents
from app.data.tickets import ITtickets
from app.data.datasets import Datasets
from app.services.user_service import Userservice, DATASETS_CSV, IT_TICKETS_CSV, CYBER_INCIDENTS_CSV

def setup_database():
    print("=" * 60)
    print("Week 8: Database Demo")
    print("=" * 60)

    # 1. delete database
    delete_database()

    conn = connect_database()
    create_all_tables(conn)

    user_service = Userservice(conn)

    # 2. Migrate users
    migrated = user_service.migrate_users_from_file()
    print(f"Users migrated: {migrated}")

    # 3. move csv data
    print("Moving CSV data")
    user_service.load_csv_to_table(DATASETS_CSV, "datasets_metadata")
    user_service.load_csv_to_table(IT_TICKETS_CSV, "it_tickets")
    user_service.load_csv_to_table(CYBER_INCIDENTS_CSV, "cyber_incidents")

    #verify table exists
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:", tables)

    conn.close()

    # 4. Test authentication
def test_user_auth():
    print("\n TESTING USER AUTHENTICATION")

    conn = connect_database()
    user_service = Userservice(conn)

    success, msg = user_service.register_user("alice", "SecurePass123!", "analyst")
    print(msg)
    success, msg = user_service.login_user("alice", "SecurePass123!")
    print(msg)
    conn.close()

    # 5. Test CRUD
def test_incident_crud():
    print("\n TESTING INCIDENT CRUD")
    conn = connect_database()
    incident = Cyberincidents(conn)

    incident_id = incident.insert_incident(
        "2024-11-05",
        "Phishing",
        "High",
        "Open",
        "Suspicious email detected",
        "alice"
    )
    print(f"Created incident #{incident_id}")

    df = incident.get_all_incidents()
    print(f"Total incidents before update: {len(df)}")

    rows_updated = incident.update_incident_status(incident_id,"In Progress")
    print(f"Updated status for incident #{incident_id}. Rows modified {rows_updated}")

    df = incident.get_all_incidents()
    print(f"Total incidents after update: {len(df)}")

    rows_deleted = incident.delete_incident_status (incident_id)
    print(f"Deleted incidents #{incident_id}. Rows deleted {rows_deleted}")

    df = incident.get_all_incidents()
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
        print(f"{user[0]:<5} {user[1]:<15} {user[2]:<10}") #user id, username, user role

    print(f"\nTotal users: {len(users)}")
    conn.close()

def run_analytical_queries():
    #analytical queries for cyber incidents
    conn = connect_database()

    incident = Cyberincidents(conn)
    ticket = ITtickets(conn)
    dataset = Datasets(conn)

    print("\n Incidents by Type:")
    print(incident.get_incidents_by_type_count())

    print("\n High Severity Incidents by Status:")
    print (incident.get_high_severity_by_status())

    print("\n Incident Types with Many Cases (>5):")
    print(incident.get_incidents_type_with_many_cases())

    #analytical queries for IT tickets

    print("\n Tickets by Status:")
    print(ticket.get_tickets_by_status_count())

    print("\n High severity by Priority:")
    print(ticket.get_high_severity_by_priority())

    print("\n Assigned cases:")
    print(ticket.get_assigned_to_with_many_cases())

    #analytical queries for datasets metadata

    print("\n Large datasets by uploader:")
    print(dataset.get_dataset_by_uploader())

    conn.close()

if __name__ == "__main__":
    setup_database()
    verify_user_migration()
    test_user_auth()
    test_incident_crud()
    run_analytical_queries()