
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "database/calibration_management.db"


def connect_db():
    return sqlite3.connect(DB_PATH)


# 1. Display first 10 Calibration Events
def display_events():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT calibration_event_id, asset_id,
                   work_order_id, performed_at, result,
                   measured_value, unit, event_state
            FROM CalibrationEvent
            ORDER BY calibration_event_id
            LIMIT 10
        """)

        records = cursor.fetchall()

        print("\nFIRST 10 CALIBRATION EVENTS")
        print("-" * 90)

        for row in records:
            print(row)

        cursor.execute("SELECT COUNT(*) FROM CalibrationEvent")
        print("\nTotal Calibration Events:", cursor.fetchone()[0])

    finally:
        conn.close()


# 2. Search by Calibration Event ID
def search_by_event_id():
    event_id = input("Enter Calibration Event ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM CalibrationEvent
            WHERE calibration_event_id = ?
        """, (event_id,))

        record = cursor.fetchone()

        if record:
            print("\nCALIBRATION EVENT DETAILS")
            print("-" * 50)

            columns = [description[0] for description in cursor.description]

            for column, value in zip(columns, record):
                print(f"{column}: {value}")
        else:
            print("Calibration Event not found.")

    finally:
        conn.close()


# 3. Search by Asset ID
def search_by_asset_id():
    asset_id = input("Enter Asset ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT calibration_event_id, asset_id,
                   work_order_id, performed_at, result,
                   measured_value, unit, event_state
            FROM CalibrationEvent
            WHERE asset_id = ?
            ORDER BY performed_at DESC
        """, (asset_id,))

        records = cursor.fetchall()

        if records:
            print("\nCALIBRATION EVENTS FOR:", asset_id)

            for row in records:
                print(row)
        else:
            print("No calibration events found.")

    finally:
        conn.close()


# 4. Display events by result
def display_by_result():
    result = input("Enter Result (Pass/Fail): ").strip().capitalize()

    if result not in ("Pass", "Fail"):
        print("Invalid result. Enter Pass or Fail.")
        return

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT calibration_event_id, asset_id,
                   work_order_id, performed_at,
                   result, measured_value, unit
            FROM CalibrationEvent
            WHERE result = ?
            ORDER BY calibration_event_id
            LIMIT 10
        """, (result,))

        records = cursor.fetchall()

        if records:
            print("\nFIRST 10 CALIBRATION EVENTS WITH RESULT:", result)

            for row in records:
                print(row)
        else:
            print("No calibration events found.")

        cursor.execute("""
            SELECT COUNT(*)
            FROM CalibrationEvent
            WHERE result = ?
        """, (result,))

        print("\nTotal matching events:", cursor.fetchone()[0])

    finally:
        conn.close()


# 5. Create new Calibration Event
def create_calibration_event():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        asset_id = input("Enter Asset ID: ").strip()

        cursor.execute(
            "SELECT 1 FROM Asset WHERE asset_id = ?",
            (asset_id,)
        )

        if cursor.fetchone() is None:
            print("Invalid Asset ID.")
            return

        plan_id = input("Enter Calibration Plan ID: ").strip()

        cursor.execute("""
            SELECT 1 FROM CalibrationPlan
            WHERE calibration_plan_id = ? AND asset_id = ?
        """, (plan_id, asset_id))

        if cursor.fetchone() is None:
            print("Invalid Calibration Plan ID for this Asset.")
            return

        work_order_id = input("Enter Work Order ID: ").strip()

        cursor.execute("""
            SELECT 1 FROM WorkOrder
            WHERE work_order_id = ? AND asset_id = ?
        """, (work_order_id, asset_id))

        if cursor.fetchone() is None:
            print("Invalid Work Order ID for this Asset.")
            return

        supplier_id = input("Enter Supplier ID: ").strip()

        cursor.execute("""
            SELECT 1 FROM Supplier WHERE supplier_id = ?
        """, (supplier_id,))

        if cursor.fetchone() is None:
            print("Invalid Supplier ID.")
            return

        performed_at = input(
            "Enter Performed Date (YYYY-MM-DD): "
        ).strip()

        datetime.strptime(performed_at, "%Y-%m-%d")

        result = input("Enter Result (Pass/Fail): ").strip().capitalize()

        if result not in ("Pass", "Fail"):
            print("Result must be Pass or Fail.")
            return

        measured_value = float(input("Enter Measured Value: "))
        unit = input("Enter Unit: ").strip()
        tolerance = float(input("Enter Tolerance: "))

        if tolerance < 0:
            print("Tolerance cannot be negative.")
            return

        technician_id = input("Enter Technician ID: ").strip()
        event_state = input("Enter Event State: ").strip()

        if not unit or not technician_id or not event_state:
            print("Unit, Technician ID and Event State are required.")
            return

        
        # Generate Event ID
        year = datetime.strptime(performed_at, "%Y-%m-%d").year

        cursor.execute("""
            SELECT calibration_event_id
            FROM CalibrationEvent
            WHERE asset_id = ?
            AND calibration_event_id LIKE ?
        """, (asset_id, f"CAL-{asset_id}-{year}-%"))

        existing_ids = []

        for row in cursor.fetchall():
            try:
                existing_ids.append(int(row[0].split("-")[-1]))
            except ValueError:
                continue

        next_number = max(existing_ids, default=0) + 1

        event_id = f"CAL-{asset_id}-{year}-{next_number:06d}"


        # Insert event
        cursor.execute("""
            INSERT INTO CalibrationEvent (
                calibration_event_id,
                asset_id,
                calibration_plan_id,
                work_order_id,
                supplier_id,
                performed_at,
                result,
                measured_value,
                unit,
                tolerance,
                technician_id,
                event_state
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            asset_id,
            plan_id,
            work_order_id,
            supplier_id,
            performed_at,
            result,
            measured_value,
            unit,
            tolerance,
            technician_id,
            event_state
        ))

       
        # Update Calibration Plan after successful closed calibration
        if result == "Pass" and event_state.strip().lower() == "closed":

            cursor.execute("""
                SELECT interval_days
                FROM CalibrationPlan
                WHERE calibration_plan_id = ?
            """, (plan_id,))

            plan = cursor.fetchone()

            if plan:
                interval_days = int(plan[0])

                performed_date = datetime.strptime(
                    performed_at, "%Y-%m-%d"
                )

                next_due_date = performed_date + timedelta(
                    days=interval_days
                )

                cursor.execute("""
                    UPDATE CalibrationPlan
                    SET last_calibration_at = ?,
                        next_due_at = ?
                    WHERE calibration_plan_id = ?
                """, (
                    performed_at,
                    next_due_date.strftime("%Y-%m-%dT00:00:00+00:00"),
                    plan_id
                ))

                print("Calibration Plan updated successfully!")

        conn.commit()

        print("\nCalibration Event created successfully!")
        print("New Calibration Event ID:", event_id)


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
        print("\n===== CALIBRATION EVENT MANAGEMENT =====")
        print("1. Display First 10 Calibration Events")
        print("2. Search by Calibration Event ID")
        print("3. Search by Asset ID")
        print("4. Display Events by Result")
        print("5. Create New Calibration Event")
        print("6. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            display_events()

        elif choice == "2":
            search_by_event_id()

        elif choice == "3":
            search_by_asset_id()

        elif choice == "4":
            display_by_result()

        elif choice == "5":
            create_calibration_event()

        elif choice == "6":
            print("Exiting Calibration Event Management.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
