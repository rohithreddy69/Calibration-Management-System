
import sqlite3
from datetime import datetime

DB_PATH = "database/calibration_management.db"


def connect_db():
    return sqlite3.connect(DB_PATH)


def display_certificates():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT certificate_id, calibration_event_id, asset_id,
               supplier_id, issued_at, valid_from, valid_to,
               certificate_status
        FROM Certificate
        ORDER BY certificate_id
        LIMIT 10
    """)

    rows = cursor.fetchall()

    print("\nFIRST 10 CERTIFICATES")
    print("-" * 100)

    for row in rows:
        print(row)

    cursor.execute("SELECT COUNT(*) FROM Certificate")
    total = cursor.fetchone()[0]

    print("\nTotal Certificates:", total)

    conn.close()


def search_by_certificate_id():
    certificate_id = input("Enter Certificate ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM Certificate
        WHERE certificate_id = ?
    """, (certificate_id,))

    row = cursor.fetchone()

    if row:
        columns = [description[0] for description in cursor.description]

        print("\nCERTIFICATE DETAILS")
        print("-" * 50)

        for column, value in zip(columns, row):
            print(f"{column}: {value}")
    else:
        print("Certificate not found.")

    conn.close()


def search_by_asset_id():
    asset_id = input("Enter Asset ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT certificate_id, calibration_event_id,
               supplier_id, issued_at, valid_from,
               valid_to, certificate_status
        FROM Certificate
        WHERE asset_id = ?
        ORDER BY issued_at DESC
    """, (asset_id,))

    rows = cursor.fetchall()

    print("\nCERTIFICATES FOR:", asset_id)
    print("-" * 100)

    if rows:
        for row in rows:
            print(row)
    else:
        print("No certificates found for this Asset ID.")

    conn.close()


def search_by_calibration_event_id():
    event_id = input("Enter Calibration Event ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM Certificate
        WHERE calibration_event_id = ?
    """, (event_id,))

    row = cursor.fetchone()

    if row:
        columns = [description[0] for description in cursor.description]

        print("\nCERTIFICATE DETAILS")
        print("-" * 50)

        for column, value in zip(columns, row):
            print(f"{column}: {value}")
    else:
        print("Certificate not found for this Calibration Event.")

    conn.close()


def display_by_status():
    status = input("Enter Certificate Status: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT certificate_id, calibration_event_id,
               asset_id, supplier_id, issued_at,
               valid_from, valid_to
        FROM Certificate
        WHERE certificate_status = ?
        ORDER BY certificate_id
        LIMIT 10
    """, (status,))

    rows = cursor.fetchall()

    print("\nFIRST 10 CERTIFICATES WITH STATUS:", status)
    print("-" * 100)

    for row in rows:
        print(row)

    cursor.execute("""
        SELECT COUNT(*) FROM Certificate
        WHERE certificate_status = ?
    """, (status,))

    total = cursor.fetchone()[0]

    print("\nTotal matching certificates:", total)

    conn.close()


def validate_date(date_value):
    try:
        datetime.fromisoformat(date_value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def create_certificate():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        event_id = input("Enter Calibration Event ID: ").strip()

        # Check whether the calibration event exists
        cursor.execute("""
            SELECT asset_id, supplier_id
            FROM CalibrationEvent
            WHERE calibration_event_id = ?
        """, (event_id,))

        event = cursor.fetchone()

        if event is None:
            print("Invalid Calibration Event ID.")
            return

        asset_id = event[0]
        supplier_id = event[1]

        # Check whether a certificate already exists
        cursor.execute("""
            SELECT 1 FROM Certificate
            WHERE calibration_event_id = ?
        """, (event_id,))

        if cursor.fetchone() is not None:
            print("A certificate already exists for this Calibration Event.")
            return

        # Generate Certificate ID
        certificate_id = f"CERT-{event_id}"

        issued_at = input(
            "Enter Issued Date (YYYY-MM-DD): "
        ).strip()

        valid_from = input(
            "Enter Valid From Date (YYYY-MM-DD): "
        ).strip()

        valid_to = input(
            "Enter Valid To Date (YYYY-MM-DD) or press Enter for NULL: "
        ).strip()

        if not validate_date(issued_at) or not validate_date(valid_from):
            print("Invalid date format.")
            return

        if valid_to and not validate_date(valid_to):
            print("Invalid Valid To date format.")
            return

        if valid_to:
            from_date = datetime.fromisoformat(valid_from.replace("Z", "+00:00"))
            to_date = datetime.fromisoformat(valid_to.replace("Z", "+00:00"))

            if to_date < from_date:
                print("Valid To date cannot be earlier than Valid From date.")
                return

        certificate_status = input(
            "Enter Certificate Status: "
        ).strip()

        if not certificate_status:
            print("Certificate Status is required.")
            return

        document_ref = input(
            "Enter Document Reference (press Enter for automatic reference): "
        ).strip()

        if not document_ref:
            document_ref = f"docs/{event_id}.pdf"

        # Insert Certificate
        cursor.execute("""
            INSERT INTO Certificate (
                certificate_id,
                calibration_event_id,
                asset_id,
                supplier_id,
                issued_at,
                valid_from,
                valid_to,
                certificate_status,
                document_ref
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            certificate_id,
            event_id,
            asset_id,
            supplier_id,
            issued_at,
            valid_from,
            valid_to if valid_to else None,
            certificate_status,
            document_ref
        ))

        conn.commit()

        print("\nCertificate created successfully!")
        print("New Certificate ID:", certificate_id)

    except ValueError:
        print("Invalid date entered.")

    except sqlite3.IntegrityError as error:
        print("Database error:", error)

    except sqlite3.Error as error:
        print("Database error:", error)

    finally:
        conn.close()


def main():
    while True:
        print("\n===== CERTIFICATE MANAGEMENT =====")
        print("1. Display First 10 Certificates")
        print("2. Search by Certificate ID")
        print("3. Search by Asset ID")
        print("4. Search by Calibration Event ID")
        print("5. Display Certificates by Status")
        print("6. Create New Certificate")
        print("7. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            display_certificates()

        elif choice == "2":
            search_by_certificate_id()

        elif choice == "3":
            search_by_asset_id()

        elif choice == "4":
            search_by_calibration_event_id()

        elif choice == "5":
            display_by_status()

        elif choice == "6":
            create_certificate()

        elif choice == "7":
            print("Exiting Certificate Management.")
            break

        else:
            print("Invalid choice. Please enter 1 to 7.")


if __name__ == "__main__":
    main()
