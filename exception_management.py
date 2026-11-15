
import sqlite3
from datetime import datetime

DB_PATH = "database/calibration_management.db"


def connect_db():
    return sqlite3.connect(DB_PATH)


# 1. Display first 10 exceptions
def display_exceptions():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Exception
        ORDER BY exception_id
        LIMIT 10
    """)

    records = cursor.fetchall()

    print("\nFIRST 10 EXCEPTIONS")
    print("-" * 80)

    for record in records:
        print(record)

    cursor.execute("SELECT COUNT(*) FROM Exception")
    total = cursor.fetchone()[0]

    print("\nTotal Exceptions:", total)

    conn.close()


# 2. Search by Exception ID
def search_by_exception_id():
    exception_id = input("Enter Exception ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Exception
        WHERE exception_id = ?
    """, (exception_id,))

    record = cursor.fetchone()

    if record:
        columns = [description[0] for description in cursor.description]

        print("\nEXCEPTION DETAILS")
        print("-" * 50)

        for column, value in zip(columns, record):
            print(f"{column}: {value}")
    else:
        print("Exception not found.")

    conn.close()


# 3. Search by Asset ID
def search_by_asset_id():
    asset_id = input("Enter Asset ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Exception
        WHERE asset_id = ?
        ORDER BY requested_at DESC
    """, (asset_id,))

    records = cursor.fetchall()

    if records:
        print("\nEXCEPTIONS FOR ASSET:", asset_id)
        print("-" * 80)

        for record in records:
            print(record)

        print("\nTotal matching records:", len(records))
    else:
        print("No exceptions found for this Asset ID.")

    conn.close()


# 4. Display exceptions by status
def display_by_status():
    status = input("Enter Exception Status: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Exception
        WHERE status = ?
        ORDER BY exception_id
        LIMIT 10
    """, (status,))

    records = cursor.fetchall()

    print("\nFIRST 10 EXCEPTIONS WITH STATUS:", status)
    print("-" * 80)

    for record in records:
        print(record)

    cursor.execute("""
        SELECT COUNT(*)
        FROM Exception
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


# Generate Exception ID

def generate_exception_id(cursor):
    current_year = datetime.now().year

    cursor.execute("""
        SELECT exception_id
        FROM Exception
        WHERE exception_id LIKE ?
    """, (f"EXC-{current_year}-%",))

    records = cursor.fetchall()

    numbers = []

    for record in records:
        try:
            numbers.append(int(record[0].split("-")[-1]))
        except ValueError:
            continue

    next_number = max(numbers, default=0) + 1

    return f"EXC-{current_year}-{next_number:06d}"


# 5. Create new exception
def create_exception():
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

        exception_type = input("Enter Exception Type: ").strip()

        requested_at = input(
            "Enter Requested At (YYYY-MM-DD or ISO timestamp): "
        ).strip()

        approved_by = input("Enter Approved By (or press Enter): ").strip()

        approved_at = input(
            "Enter Approved At (or press Enter): "
        ).strip()

        extension_due_at = input(
            "Enter Extension Due Date (YYYY-MM-DD or ISO timestamp): "
        ).strip()

        status = input("Enter Status: ").strip()

        reason = input("Enter Reason: ").strip()

        if not exception_type or not extension_due_at or not status or not reason:
            print("Required fields cannot be empty.")
            return

        if not validate_datetime(requested_at):
            print("Invalid Requested At date/time.")
            return

        if not validate_datetime(extension_due_at):
            print("Invalid Extension Due Date.")
            return

        if approved_at and not validate_datetime(approved_at):
            print("Invalid Approved At date/time.")
            return

        if approved_by and not approved_at:
            print("Approved At is required when Approved By is entered.")
            return

        if approved_at and not approved_by:
            print("Approved By is required when Approved At is entered.")
            return

        exception_id = generate_exception_id(cursor)

        cursor.execute("""
            INSERT INTO Exception (
                exception_id,
                asset_id,
                exception_type,
                requested_at,
                approved_by,
                approved_at,
                extension_due_at,
                status,
                reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            exception_id,
            asset_id,
            exception_type,
            requested_at,
            approved_by or None,
            approved_at or None,
            extension_due_at,
            status,
            reason
        ))

        conn.commit()

        print("\nException created successfully!")
        print("New Exception ID:", exception_id)

    except sqlite3.IntegrityError as e:
        print("Database integrity error:", e)

    except sqlite3.Error as e:
        print("Database error:", e)

    finally:
        conn.close()


# Main menu
def main():
    while True:
        print("\n===== EXCEPTION MANAGEMENT =====")
        print("1. Display First 10 Exceptions")
        print("2. Search by Exception ID")
        print("3. Search by Asset ID")
        print("4. Display Exceptions by Status")
        print("5. Create New Exception")
        print("6. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            display_exceptions()

        elif choice == "2":
            search_by_exception_id()

        elif choice == "3":
            search_by_asset_id()

        elif choice == "4":
            display_by_status()

        elif choice == "5":
            create_exception()

        elif choice == "6":
            print("Exiting Exception Management.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
