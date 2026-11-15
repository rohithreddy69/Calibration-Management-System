
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import Counter

DB_PATH = Path(__file__).resolve().parent / "database" / "calibration_management.db"


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def display_corrective_actions():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM CorrectiveAction
        ORDER BY corrective_action_id
        LIMIT 10
    """)

    records = cursor.fetchall()

    print("\nFIRST 10 CORRECTIVE ACTIONS")
    print("-" * 100)

    for record in records:
        print(record)

    cursor.execute("SELECT COUNT(*) FROM CorrectiveAction")
    total = cursor.fetchone()[0]

    print("\nTotal Corrective Actions:", total)
    conn.close()


def search_by_corrective_action_id():
    action_id = input("Enter Corrective Action ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM CorrectiveAction
        WHERE corrective_action_id = ?
    """, (action_id,))

    record = cursor.fetchone()

    if record:
        columns = [description[0] for description in cursor.description]

        print("\nCORRECTIVE ACTION DETAILS")
        print("-" * 50)

        for column, value in zip(columns, record):
            print(f"{column}: {value}")
    else:
        print("Corrective Action not found.")

    conn.close()


def search_by_asset_id():
    asset_id = input("Enter Asset ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM CorrectiveAction
        WHERE asset_id = ?
        ORDER BY created_at DESC
    """, (asset_id,))

    records = cursor.fetchall()

    print("\nCORRECTIVE ACTIONS FOR ASSET:", asset_id)
    print("-" * 100)

    for record in records:
        print(record)

    print("\nTotal matching records:", len(records))
    conn.close()


def display_by_status():
    status = input(
        "Enter Action Status (Open/InProgress/Completed): "
    ).strip()

    if status not in ("Open", "InProgress", "Completed"):
        print("Invalid status.")
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM CorrectiveAction
        WHERE action_status = ?
        ORDER BY corrective_action_id
        LIMIT 10
    """, (status,))

    records = cursor.fetchall()

    print("\nFIRST 10 CORRECTIVE ACTIONS WITH STATUS:", status)
    print("-" * 100)

    for record in records:
        print(record)

    cursor.execute("""
        SELECT COUNT(*)
        FROM CorrectiveAction
        WHERE action_status = ?
    """, (status,))

    total = cursor.fetchone()[0]

    print("\nTotal matching records:", total)
    conn.close()


def validate_datetime(value):
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False



def generate_corrective_action_id(cursor):
    cursor.execute("""
        SELECT corrective_action_id
        FROM CorrectiveAction
        WHERE corrective_action_id LIKE 'CA-%'
    """)

    records = cursor.fetchall()
    numbers = []

    for record in records:
        try:
            number = int(record[0].split("-")[-1])
            numbers.append(number)
        except ValueError:
            continue

    next_number = max(numbers, default=0) + 1

    while True:
        new_id = f"CA-{next_number:06d}"

        cursor.execute("""
            SELECT 1
            FROM CorrectiveAction
            WHERE corrective_action_id = ?
        """, (new_id,))

        if cursor.fetchone() is None:
            return new_id

        next_number += 1


def create_corrective_action():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        calibration_event_id = input(
            "Enter Calibration Event ID: "
        ).strip()

        cursor.execute("""
            SELECT asset_id
            FROM CalibrationEvent
            WHERE calibration_event_id = ?
        """, (calibration_event_id,))

        event = cursor.fetchone()

        if event is None:
            print("Calibration Event not found.")
            return

        asset_id = event[0]
        print("Linked Asset ID:", asset_id)

        action_type = input(
            "Enter Action Type (ImpactAssessment/Repair/Recalibration): "
        ).strip()

        if action_type not in (
            "ImpactAssessment", "Repair", "Recalibration"
        ):
            print("Invalid Action Type.")
            return

        created_at = input(
            "Enter Created At (YYYY-MM-DD or ISO timestamp): "
        ).strip()

        if not validate_datetime(created_at):
            print("Invalid date/time format.")
            return

        impact_level = input(
            "Enter Impact Level (Low/Medium/High): "
        ).strip()

        if impact_level not in ("Low", "Medium", "High"):
            print("Invalid Impact Level.")
            return

        action_status = input(
            "Enter Action Status (Open/InProgress/Completed): "
        ).strip()

        if action_status not in ("Open", "InProgress", "Completed"):
            print("Invalid Action Status.")
            return

        description = input(
            "Enter Description: "
        ).strip()

        if not description:
            print("Description cannot be empty.")
            return

        corrective_action_id = generate_corrective_action_id(cursor)
        print("Next Corrective Action ID:", corrective_action_id)

        cursor.execute("""
            INSERT INTO CorrectiveAction (
                corrective_action_id,
                calibration_event_id,
                asset_id,
                action_type,
                created_at,
                impact_level,
                action_status,
                description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            corrective_action_id,
            calibration_event_id,
            asset_id,
            action_type,
            created_at,
            impact_level,
            action_status,
            description
        ))

        conn.commit()

        print("\nCorrective Action created successfully!")
        print("New Corrective Action ID:", corrective_action_id)

    except sqlite3.IntegrityError as error:
        conn.rollback()
        print("Database constraint error:", error)

    except sqlite3.Error as error:
        conn.rollback()
        print("Database error:", error)

    finally:
        conn.close()


def main():
    while True:
        print("\n===== CORRECTIVE ACTION MANAGEMENT =====")
        print("1. Display First 10 Corrective Actions")
        print("2. Search by Corrective Action ID")
        print("3. Search by Asset ID")
        print("4. Display Corrective Actions by Status")
        print("5. Create New Corrective Action")
        print("6. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            display_corrective_actions()

        elif choice == "2":
            search_by_corrective_action_id()

        elif choice == "3":
            search_by_asset_id()

        elif choice == "4":
            display_by_status()

        elif choice == "5":
            create_corrective_action()

        elif choice == "6":
            print("Exiting Corrective Action Management.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
