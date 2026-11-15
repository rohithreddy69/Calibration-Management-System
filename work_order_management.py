
import sqlite3
from datetime import datetime

DB_PATH = "database/calibration_management.db"


def connect_db():
    return sqlite3.connect(DB_PATH)


# 1. Display first 10 work orders
def display_work_orders():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT work_order_id, asset_id, work_order_type,
                   scheduled_start, scheduled_end, status
            FROM WorkOrder
            ORDER BY work_order_id
            LIMIT 10
        """)

        records = cursor.fetchall()

        print("\nFIRST 10 WORK ORDERS")
        print("-" * 90)

        for row in records:
            print(
                f"Work Order: {row[0]} | Asset: {row[1]} | "
                f"Type: {row[2]} | Start: {row[3]} | "
                f"End: {row[4]} | Status: {row[5]}"
            )

        cursor.execute("SELECT COUNT(*) FROM WorkOrder")
        print("\nTotal Work Orders:", cursor.fetchone()[0])

    finally:
        conn.close()


# 2. Search by Work Order ID
def search_by_work_order_id():
    work_order_id = input("Enter Work Order ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM WorkOrder
            WHERE work_order_id = ?
        """, (work_order_id,))

        record = cursor.fetchone()

        if record:
            print("\nWORK ORDER DETAILS")
            print("-" * 50)

            columns = [
                description[0]
                for description in cursor.description
            ]

            for column, value in zip(columns, record):
                print(f"{column}: {value}")
        else:
            print("Work Order not found.")

    finally:
        conn.close()


# 3. Search by Asset ID
def search_by_asset_id():
    asset_id = input("Enter Asset ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT work_order_id, asset_id, work_order_type,
                   scheduled_start, scheduled_end, status
            FROM WorkOrder
            WHERE asset_id = ?
            ORDER BY work_order_id
        """, (asset_id,))

        records = cursor.fetchall()

        if records:
            print("\nWORK ORDERS FOR", asset_id)

            for row in records:
                print(row)
        else:
            print("No work orders found for this Asset ID.")

    finally:
        conn.close()


# 4. Display Work Orders by Status
def display_by_status():
    status = input("Enter Work Order Status: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT work_order_id, asset_id, work_order_type,
                   scheduled_start, scheduled_end, status
            FROM WorkOrder
            WHERE LOWER(status) = LOWER(?)
            ORDER BY work_order_id
            LIMIT 10
        """, (status,))

        records = cursor.fetchall()

        if records:
            print("\nFIRST 10 WORK ORDERS WITH STATUS:", status)

            for row in records:
                print(row)
        else:
            print("No work orders found with this status.")

        cursor.execute("""
            SELECT COUNT(*)
            FROM WorkOrder
            WHERE LOWER(status) = LOWER(?)
        """, (status,))

        total = cursor.fetchone()[0]

        print("\nTotal matching work orders:", total)

    finally:
        conn.close()


# 5. Create New Work Order
def create_work_order():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Check available Asset IDs
        cursor.execute("""
            SELECT asset_id FROM Asset
        """)
        assets = [row[0] for row in cursor.fetchall()]

        # Check available Supplier IDs
        cursor.execute("""
            SELECT supplier_id FROM Supplier
        """)
        suppliers = [row[0] for row in cursor.fetchall()]

        asset_id = input("Enter Asset ID: ").strip()

        if asset_id not in assets:
            print("Invalid Asset ID.")
            return

        supplier_id = input("Enter Supplier ID: ").strip()

        if supplier_id not in suppliers:
            print("Invalid Supplier ID.")
            return

        work_order_type = input("Enter Work Order Type: ").strip()

        if not work_order_type:
            print("Work Order Type cannot be empty.")
            return

        scheduled_start = input(
            "Enter Scheduled Start (YYYY-MM-DD): "
        ).strip()

        scheduled_end = input(
            "Enter Scheduled End (YYYY-MM-DD): "
        ).strip()

        # Validate dates
        start_date = datetime.strptime(
            scheduled_start, "%Y-%m-%d"
        ).date()

        end_date = datetime.strptime(
            scheduled_end, "%Y-%m-%d"
        ).date()

        if end_date < start_date:
            print("Scheduled End cannot be before Scheduled Start.")
            return

        downtime_hours = float(
            input("Enter Downtime Hours: ")
        )

        if downtime_hours < 0:
            print("Downtime cannot be negative.")
            return

        status = input("Enter Status: ").strip()

        if not status:
            print("Status cannot be empty.")
            return

        # Generate Work Order ID in the correct format
        current_year = datetime.now().year
        year_prefix = f"WO-{current_year}-"

        cursor.execute("""
            SELECT work_order_id
            FROM WorkOrder
            WHERE work_order_id LIKE ?
        """, (year_prefix + "%",))

        existing_ids = []

        for row in cursor.fetchall():
            try:
                number = int(row[0].split("-")[-1])
                existing_ids.append(number)
            except ValueError:
                continue

        next_number = max(existing_ids, default=0) + 1

        work_order_id = (
            f"WO-{current_year}-{next_number:06d}"
        )

        created_at = datetime.now().isoformat()

        # Insert new Work Order
        cursor.execute("""
            INSERT INTO WorkOrder (
                work_order_id,
                asset_id,
                work_order_type,
                created_at,
                scheduled_start,
                scheduled_end,
                actual_start,
                actual_end,
                downtime_hours,
                status,
                supplier_id
            )
            VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?)
        """, (
            work_order_id,
            asset_id,
            work_order_type,
            created_at,
            scheduled_start,
            scheduled_end,
            downtime_hours,
            status,
            supplier_id
        ))

        conn.commit()

        print("\nWork Order created successfully!")
        print("New Work Order ID:", work_order_id)

    except ValueError:
        print("Invalid date or number. Please enter valid values.")

    except sqlite3.IntegrityError as error:
        print("Database error:", error)

    except sqlite3.Error as error:
        print("Database error:", error)

    finally:
        conn.close()


# Main Menu
def main():
    while True:
        print("\n===== WORK ORDER MANAGEMENT =====")
        print("1. Display First 10 Work Orders")
        print("2. Search by Work Order ID")
        print("3. Search by Asset ID")
        print("4. Display Work Orders by Status")
        print("5. Create New Work Order")
        print("6. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            display_work_orders()

        elif choice == "2":
            search_by_work_order_id()

        elif choice == "3":
            search_by_asset_id()

        elif choice == "4":
            display_by_status()

        elif choice == "5":
            create_work_order()

        elif choice == "6":
            print("Exiting Work Order Management.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
