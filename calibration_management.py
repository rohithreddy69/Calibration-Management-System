
import sqlite3
from datetime import date, timedelta

DB_PATH = "database/calibration_management.db"


def connect_db():
    return sqlite3.connect(DB_PATH)


def get_calibration_status(next_due_at, grace_days):
    try:
        due_date = date.fromisoformat(str(next_due_at)[:10])
    except (ValueError, TypeError):
        return "INVALID DATE"

    today = date.today()

    if today > due_date + timedelta(days=grace_days):
        return "OVERDUE"
    elif today > due_date:
        return "GRACE PERIOD"
    elif due_date <= today + timedelta(days=30):
        return "DUE SOON"
    else:
        return "ON TRACK"


def get_all_plans():
    connection = connect_db()

    records = connection.execute("""
        SELECT
            cp.calibration_plan_id,
            cp.asset_id,
            a.asset_name,
            cp.interval_days,
            cp.last_calibration_at,
            cp.next_due_at,
            cp.grace_days,
            cp.plan_state
        FROM CalibrationPlan cp
        JOIN Asset a ON cp.asset_id = a.asset_id
        ORDER BY cp.asset_id
    """).fetchall()

    connection.close()
    return records


def display_plans():
    records = get_all_plans()

    print("\nFIRST 10 CALIBRATION PLANS")
    print("-" * 75)

    for record in records[:10]:
        status = get_calibration_status(
            record[5], record[6]
        )

        print(
            f"Plan ID: {record[0]} | "
            f"Asset ID: {record[1]} | "
            f"Name: {record[2]} | "
            f"Next Due: {record[5]} | "
            f"Status: {status}"
        )

    print("\nTotal Calibration Plans:", len(records))


def search_by_asset_id():
    asset_id = input("Enter Asset ID: ").strip()

    records = get_all_plans()

    found = False

    for record in records:
        if record[1] == asset_id:
            found = True

            status = get_calibration_status(
                record[5], record[6]
            )

            print("\nCALIBRATION PLAN DETAILS")
            print("Plan ID:", record[0])
            print("Asset ID:", record[1])
            print("Instrument Name:", record[2])
            print("Calibration Interval:", record[3], "days")
            print("Last Calibration:", record[4])
            print("Next Due Date:", record[5])
            print("Grace Days:", record[6])
            print("Plan State:", record[7])
            print("Calibration Status:", status)

    if not found:
        print("No calibration plan found for this Asset ID.")


def show_upcoming_calibrations():
    records = get_all_plans()
    today = date.today()
    end_date = today + timedelta(days=30)

    print("\nUPCOMING CALIBRATIONS (NEXT 30 DAYS)")
    print("-" * 75)

    count = 0

    for record in records:
        try:
            due_date = date.fromisoformat(str(record[5])[:10])
        except (ValueError, TypeError):
            continue

        if today <= due_date <= end_date:
            count += 1
            print(
                f"Asset ID: {record[1]} | "
                f"Name: {record[2]} | "
                f"Due Date: {record[5]}"
            )

    print("\nTotal Upcoming Calibrations:", count)


def show_overdue_calibrations():
    records = get_all_plans()

    print("\nOVERDUE CALIBRATIONS")
    print("-" * 75)

    count = 0

    for record in records:
        status = get_calibration_status(
            record[5], record[6]
        )

        if status == "OVERDUE":
            count += 1

            try:
                due_date = date.fromisoformat(str(record[5])[:10])
                days_overdue = (date.today() - due_date).days
            except (ValueError, TypeError):
                days_overdue = "Unknown"

            print(
                f"Asset ID: {record[1]} | "
                f"Name: {record[2]} | "
                f"Due Date: {record[5]} | "
                f"Days Past Due: {days_overdue}"
            )

    print("\nTotal Overdue Calibrations:", count)


def main():
    while True:
        print("\n===== CALIBRATION MANAGEMENT SYSTEM =====")
        print("1. Display Calibration Plans")
        print("2. Search by Asset ID")
        print("3. Upcoming Calibrations")
        print("4. Overdue Calibrations")
        print("5. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            display_plans()

        elif choice == "2":
            search_by_asset_id()

        elif choice == "3":
            show_upcoming_calibrations()

        elif choice == "4":
            show_overdue_calibrations()

        elif choice == "5":
            print("Exiting Calibration Management System.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

