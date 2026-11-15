
import sqlite3
from datetime import datetime

DB_PATH = "database/calibration_management.db"


def connect_db():
    return sqlite3.connect(DB_PATH)


# 1. Display first 10 alerts
def display_alerts():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Alert
        ORDER BY alert_id
        LIMIT 10
    """)

    records = cursor.fetchall()

    print("\nFIRST 10 ALERTS")
    print("-" * 80)

    for record in records:
        print(record)

    cursor.execute("SELECT COUNT(*) FROM Alert")
    total = cursor.fetchone()[0]

    print("\nTotal Alerts:", total)

    conn.close()


# 2. Search by Alert ID
def search_by_alert_id():
    alert_id = input("Enter Alert ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Alert
        WHERE alert_id = ?
    """, (alert_id,))

    record = cursor.fetchone()

    if record:
        columns = [description[0] for description in cursor.description]

        print("\nALERT DETAILS")
        print("-" * 50)

        for column, value in zip(columns, record):
            print(f"{column}: {value}")
    else:
        print("Alert not found.")

    conn.close()


# 3. Search by Asset ID
def search_by_asset_id():
    asset_id = input("Enter Asset ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Alert
        WHERE asset_id = ?
        ORDER BY created_at DESC
    """, (asset_id,))

    records = cursor.fetchall()

    if records:
        print("\nALERTS FOR ASSET:", asset_id)
        print("-" * 80)

        for record in records:
            print(record)

        print("\nTotal matching records:", len(records))
    else:
        print("No alerts found for this Asset ID.")

    conn.close()


# 4. Display alerts by severity
def display_by_severity():
    severity = input("Enter Alert Severity: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Alert
        WHERE severity = ?
        ORDER BY alert_id
        LIMIT 10
    """, (severity,))

    records = cursor.fetchall()

    print("\nFIRST 10 ALERTS WITH SEVERITY:", severity)
    print("-" * 80)

    for record in records:
        print(record)

    cursor.execute("""
        SELECT COUNT(*)
        FROM Alert
        WHERE severity = ?
    """, (severity,))

    total = cursor.fetchone()[0]

    print("\nTotal matching records:", total)

    conn.close()


# 5. Display alerts by status
def display_by_status():
    status = input("Enter Alert Status: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Alert
        WHERE status = ?
        ORDER BY alert_id
        LIMIT 10
    """, (status,))

    records = cursor.fetchall()

    print("\nFIRST 10 ALERTS WITH STATUS:", status)
    print("-" * 80)

    for record in records:
        print(record)

    cursor.execute("""
        SELECT COUNT(*)
        FROM Alert
        WHERE status = ?
    """, (status,))

    total = cursor.fetchone()[0]

    print("\nTotal matching records:", total)

    conn.close()


# Validate date/time
def validate_datetime(value):
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


# Generate Alert ID

def generate_alert_id(cursor):
    cursor.execute("""
        SELECT alert_id
        FROM Alert
        WHERE alert_id LIKE 'ALT-%'
    """)

    records = cursor.fetchall()
    numbers = []

    for record in records:
        try:
            numbers.append(int(record[0].split("-")[-1]))
        except ValueError:
            continue

    next_number = max(numbers, default=0) + 1

    return f"ALT-{next_number:06d}"



# 6. Create new alert
def create_alert():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        asset_id = input("Enter Asset ID: ").strip()

        cursor.execute("""
            SELECT asset_id
            FROM Asset
            WHERE asset_id = ?
        """, (asset_id,))

        if not cursor.fetchone():
            print("Invalid Asset ID.")
            return

        related_record_id = input("Enter Related Record ID: ").strip()
        alert_type = input("Enter Alert Type: ").strip()
        severity = input("Enter Severity: ").strip()
        created_at = input(
            "Enter Created At (YYYY-MM-DD or ISO timestamp): "
        ).strip()
        status = input("Enter Alert Status: ").strip()

        if not all([
            related_record_id,
            alert_type,
            severity,
            created_at,
            status
        ]):
            print("All fields except Alert ID are required.")
            return

        if not validate_datetime(created_at):
            print("Invalid Created At date/time.")
            return

        alert_id = generate_alert_id(cursor)

        cursor.execute("""
            INSERT INTO Alert (
                alert_id,
                asset_id,
                related_record_id,
                alert_type,
                severity,
                created_at,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            alert_id,
            asset_id,
            related_record_id,
            alert_type,
            severity,
            created_at,
            status
        ))

        conn.commit()

        print("\nAlert created successfully!")
        print("New Alert ID:", alert_id)

    except sqlite3.IntegrityError as e:
        print("Database integrity error:", e)

    except sqlite3.Error as e:
        print("Database error:", e)

    finally:
        conn.close()


# Main menu
def main():
    while True:
        print("\n===== ALERT MANAGEMENT =====")
        print("1. Display First 10 Alerts")
        print("2. Search by Alert ID")
        print("3. Search by Asset ID")
        print("4. Display Alerts by Severity")
        print("5. Display Alerts by Status")
        print("6. Create New Alert")
        print("7. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            display_alerts()

        elif choice == "2":
            search_by_alert_id()

        elif choice == "3":
            search_by_asset_id()

        elif choice == "4":
            display_by_severity()

        elif choice == "5":
            display_by_status()

        elif choice == "6":
            create_alert()

        elif choice == "7":
            print("Exiting Alert Management.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
