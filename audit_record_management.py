
import sqlite3
from datetime import datetime

DB_PATH = "database/calibration_management.db"


def connect_db():
    return sqlite3.connect(DB_PATH)


# 1. Display first 10 audit records
def display_audit_records():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM AuditRecord
        ORDER BY audit_record_id
        LIMIT 10
    """)

    records = cursor.fetchall()

    print("\nFIRST 10 AUDIT RECORDS")
    print("-" * 80)

    for record in records:
        print(record)

    cursor.execute("SELECT COUNT(*) FROM AuditRecord")
    total = cursor.fetchone()[0]

    print("\nTotal Audit Records:", total)

    conn.close()


# 2. Search by Audit Record ID
def search_by_audit_record_id():
    audit_id = input("Enter Audit Record ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM AuditRecord
        WHERE audit_record_id = ?
    """, (audit_id,))

    record = cursor.fetchone()

    if record:
        columns = [description[0] for description in cursor.description]

        print("\nAUDIT RECORD DETAILS")
        print("-" * 50)

        for column, value in zip(columns, record):
            print(f"{column}: {value}")
    else:
        print("Audit record not found.")

    conn.close()


# 3. Search by Entity ID
def search_by_entity_id():
    entity_id = input("Enter Entity ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM AuditRecord
        WHERE entity_id = ?
        ORDER BY occurred_at DESC
    """, (entity_id,))

    records = cursor.fetchall()

    if records:
        print("\nAUDIT RECORDS FOR ENTITY:", entity_id)
        print("-" * 80)

        for record in records:
            print(record)

        print("\nTotal matching records:", len(records))
    else:
        print("No audit records found for this Entity ID.")

    conn.close()


# 4. Display records by Entity Type
def display_by_entity_type():
    entity_type = input("Enter Entity Type: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM AuditRecord
        WHERE entity_type = ?
        ORDER BY occurred_at DESC
        LIMIT 10
    """, (entity_type,))

    records = cursor.fetchall()

    print("\nFIRST 10 AUDIT RECORDS WITH ENTITY TYPE:", entity_type)
    print("-" * 80)

    for record in records:
        print(record)

    cursor.execute("""
        SELECT COUNT(*)
        FROM AuditRecord
        WHERE entity_type = ?
    """, (entity_type,))

    total = cursor.fetchone()[0]

    print("\nTotal matching records:", total)

    conn.close()


# 5. Display records by Action
def display_by_action():
    action = input("Enter Action: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM AuditRecord
        WHERE action = ?
        ORDER BY occurred_at DESC
        LIMIT 10
    """, (action,))

    records = cursor.fetchall()

    print("\nFIRST 10 AUDIT RECORDS WITH ACTION:", action)
    print("-" * 80)

    for record in records:
        print(record)

    cursor.execute("""
        SELECT COUNT(*)
        FROM AuditRecord
        WHERE action = ?
    """, (action,))

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


# Generate Audit Record ID
def generate_audit_record_id(cursor):
    cursor.execute("""
        SELECT audit_record_id
        FROM AuditRecord
        WHERE audit_record_id LIKE 'AUD-%'
    """)

    records = cursor.fetchall()
    numbers = []

    for record in records:
        try:
            numbers.append(int(record[0].split("-")[-1]))
        except ValueError:
            continue

    next_number = max(numbers, default=0) + 1

    return f"AUD-{next_number:06d}"


# 6. Create new Audit Record
def create_audit_record():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        entity_type = input("Enter Entity Type: ").strip()
        entity_id = input("Enter Entity ID: ").strip()
        action = input("Enter Action: ").strip()
        actor_id = input("Enter Actor ID: ").strip()

        occurred_at = input(
            "Enter Occurred At (YYYY-MM-DD or ISO timestamp): "
        ).strip()

        before_value = input(
            "Enter Before Value (or press Enter): "
        ).strip()

        after_value = input(
            "Enter After Value (or press Enter): "
        ).strip()

        if not all([
            entity_type,
            entity_id,
            action,
            actor_id,
            occurred_at
        ]):
            print("Required fields cannot be empty.")
            return

        if not validate_datetime(occurred_at):
            print("Invalid Occurred At date/time.")
            return

        audit_record_id = generate_audit_record_id(cursor)

        cursor.execute("""
            INSERT INTO AuditRecord (
                audit_record_id,
                entity_type,
                entity_id,
                action,
                actor_id,
                occurred_at,
                before_value,
                after_value
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            audit_record_id,
            entity_type,
            entity_id,
            action,
            actor_id,
            occurred_at,
            before_value or None,
            after_value or None
        ))

        conn.commit()

        print("\nAudit Record created successfully!")
        print("New Audit Record ID:", audit_record_id)

    except sqlite3.IntegrityError as e:
        print("Database integrity error:", e)

    except sqlite3.Error as e:
        print("Database error:", e)

    finally:
        conn.close()


# Main menu
def main():
    while True:
        print("\n===== AUDIT RECORD MANAGEMENT =====")
        print("1. Display First 10 Audit Records")
        print("2. Search by Audit Record ID")
        print("3. Search by Entity ID")
        print("4. Display Records by Entity Type")
        print("5. Display Records by Action")
        print("6. Create New Audit Record")
        print("7. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            display_audit_records()

        elif choice == "2":
            search_by_audit_record_id()

        elif choice == "3":
            search_by_entity_id()

        elif choice == "4":
            display_by_entity_type()

        elif choice == "5":
            display_by_action()

        elif choice == "6":
            create_audit_record()

        elif choice == "7":
            print("Exiting Audit Record Management.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
