
import sqlite3
from datetime import datetime

DB_PATH = "database/calibration_management.db"


def connect_db():
    return sqlite3.connect(DB_PATH)


def display_instruments():
    connection = connect_db()

    records = connection.execute("""
        SELECT asset_id, asset_name, serial_number, criticality
        FROM Asset
        ORDER BY asset_id
        LIMIT 10
    """).fetchall()

    print("\nFIRST 10 INSTRUMENTS")
    print("-" * 70)

    for record in records:
        print(
            f"Asset ID: {record[0]} | "
            f"Name: {record[1]} | "
            f"Serial No: {record[2]} | "
            f"Criticality: {record[3]}"
        )

    connection.close()


def search_by_asset_id():
    asset_id = input("Enter Asset ID: ").strip()

    connection = connect_db()

    record = connection.execute("""
        SELECT asset_id, asset_name, serial_number, criticality
        FROM Asset
        WHERE asset_id = ?
    """, (asset_id,)).fetchone()

    if record:
        print("\nInstrument Found:")
        print("Asset ID:", record[0])
        print("Name:", record[1])
        print("Serial Number:", record[2])
        print("Criticality:", record[3])
    else:
        print("No instrument found.")

    connection.close()


def search_by_name_or_serial():
    keyword = input("Enter instrument name or serial number: ").strip()

    connection = connect_db()

    records = connection.execute("""
        SELECT asset_id, asset_name, serial_number, criticality
        FROM Asset
        WHERE asset_name LIKE ? OR serial_number LIKE ?
        LIMIT 20
    """, (f"%{keyword}%", f"%{keyword}%")).fetchall()

    if records:
        print("\nSEARCH RESULTS")

        for record in records:
            print(record)
    else:
        print("No matching instruments found.")

    connection.close()


def add_instrument():
    connection = connect_db()

    print("\n===== ADD NEW INSTRUMENT =====")

    # Generate next Asset ID
    existing_ids = connection.execute(
        "SELECT asset_id FROM Asset"
    ).fetchall()

    numbers = []

    for row in existing_ids:
        try:
            numbers.append(int(row[0].split("-")[-1]))
        except ValueError:
            continue

    next_number = max(numbers, default=0) + 1
    asset_id = f"AST-{next_number:06d}"

    print("Generated Asset ID:", asset_id)

    # Display valid instrument type IDs
    types = connection.execute("""
        SELECT instrument_type_id
        FROM InstrumentType
    """).fetchall()

    print("\nAvailable Instrument Type IDs:")

    for item in types:
        print(item[0])

    instrument_type_id = input(
        "Enter Instrument Type ID: "
    ).strip()

    valid_type_ids = [item[0] for item in types]

    if instrument_type_id not in valid_type_ids:
        print("Invalid Instrument Type ID.")
        connection.close()
        return

    asset_name = input("Enter Instrument Name: ").strip()
    serial_number = input("Enter Serial Number: ").strip()
    site = input("Enter Site: ").strip()
    area = input("Enter Area: ").strip()

    criticality = input(
        "Enter Criticality (Low/Medium/High/Critical): "
    ).strip().capitalize()

    if criticality not in ["Low", "Medium", "High", "Critical"]:
        print("Invalid criticality.")
        connection.close()
        return

    commissioned_at = input(
        "Enter Commissioned Date (YYYY-MM-DD): "
    ).strip()

    try:
        datetime.strptime(commissioned_at, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format.")
        connection.close()
        return

    lifecycle_state = input(
        "Enter Lifecycle State (e.g. Active): "
    ).strip()

    if not all([
        asset_name, serial_number, site,
        area, lifecycle_state
    ]):
        print("All fields are required.")
        connection.close()
        return

    try:
        connection.execute("""
            INSERT INTO Asset (
                asset_id,
                asset_name,
                instrument_type_id,
                serial_number,
                site,
                area,
                criticality,
                commissioned_at,
                lifecycle_state
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asset_id,
            asset_name,
            instrument_type_id,
            serial_number,
            site,
            area,
            criticality,
            commissioned_at,
            lifecycle_state
        ))

        connection.commit()
        print("\nInstrument added successfully!")
        print("New Asset ID:", asset_id)

    except sqlite3.IntegrityError as error:
        print("Could not add instrument:", error)

    finally:
        connection.close()


def main():
    while True:
        print("\n===== INSTRUMENT MANAGEMENT SYSTEM =====")
        print("1. Display Instruments")
        print("2. Search by Asset ID")
        print("3. Search by Name or Serial Number")
        print("4. Add New Instrument")
        print("5. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            display_instruments()

        elif choice == "2":
            search_by_asset_id()

        elif choice == "3":
            search_by_name_or_serial()

        elif choice == "4":
            add_instrument()

        elif choice == "5":
            print("Exiting Instrument Management System.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
