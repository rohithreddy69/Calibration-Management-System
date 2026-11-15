import sqlite3
from datetime import datetime, timedelta, timezone

DB_PATH = "database/calibration_management.db"


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def display_production_use():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT production_use_id, asset_id, used_at,
            production_order_id, operation,
            calibration_due_at, use_decision
        FROM ProductionUse
        ORDER BY production_use_id
        LIMIT 10
    """)

    rows = cursor.fetchall()

    print("\nFIRST 10 PRODUCTION USE RECORDS")
    print("-" * 100)

    for row in rows:
        print(row)

    cursor.execute("SELECT COUNT(*) FROM ProductionUse")
    print("\nTotal Production Use Records:", cursor.fetchone()[0])

    conn.close()


def search_by_production_use_id():
    use_id = input("Enter Production Use ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM ProductionUse
        WHERE production_use_id = ?
    """, (use_id,))

    row = cursor.fetchone()

    if row:
        columns = [description[0] for description in cursor.description]

        print("\nPRODUCTION USE DETAILS")
        print("-" * 50)

        for column, value in zip(columns, row):
            print(f"{column}: {value}")
    else:
        print("Production Use record not found.")

    conn.close()


def search_by_asset_id():
    asset_id = input("Enter Asset ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT production_use_id, used_at,
            production_order_id, operation,
            calibration_due_at, use_decision
        FROM ProductionUse
        WHERE asset_id = ?
        ORDER BY used_at DESC
        LIMIT 10
    """, (asset_id,))

    rows = cursor.fetchall()

    print("\nPRODUCTION USE RECORDS FOR:", asset_id)
    print("-" * 100)

    for row in rows:
        print(row)

    cursor.execute("""
        SELECT COUNT(*) FROM ProductionUse
        WHERE asset_id = ?
    """, (asset_id,))

    print("\nTotal matching records:", cursor.fetchone()[0])

    conn.close()


def search_by_production_order_id():
    order_id = input("Enter Production Order ID: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM ProductionUse
        WHERE production_order_id = ?
        ORDER BY used_at DESC
        LIMIT 10
    """, (order_id,))

    rows = cursor.fetchall()

    print("\nPRODUCTION USE RECORDS FOR:", order_id)
    print("-" * 100)

    if rows:
        for row in rows:
            print(row)
    else:
        print("No records found.")

    conn.close()


def display_by_decision():
    decision = input("Enter Use Decision: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT production_use_id, asset_id, used_at,
            production_order_id, operation,
            use_decision
        FROM ProductionUse
        WHERE use_decision = ?
        ORDER BY production_use_id
        LIMIT 10
    """, (decision,))

    rows = cursor.fetchall()

    print("\nFIRST 10 RECORDS WITH DECISION:", decision)
    print("-" * 100)

    for row in rows:
        print(row)

    cursor.execute("""
        SELECT COUNT(*) FROM ProductionUse
        WHERE use_decision = ?
    """, (decision,))

    print("\nTotal matching records:", cursor.fetchone()[0])

    conn.close()


def validate_date(date_value):
    try:
        datetime.fromisoformat(date_value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False

def parse_datetime(value):
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt


def convert_policy(value):
    return str(value).strip().lower() in ("true", "1", "yes")


def get_production_use_rules(cursor, asset_id, used_at):
    used_dt = parse_datetime(used_at)

    # Find an active calibration plan effective on the use date
    cursor.execute("""
        SELECT calibration_plan_id, interval_days,
            policy_block_overdue, grace_days,
            effective_from, effective_to
        FROM CalibrationPlan
        WHERE asset_id = ?
        AND plan_state = 'Active'
    """, (asset_id,))

    plans = cursor.fetchall()
    applicable_plans = []

    for plan in plans:
        effective_from = parse_datetime(plan[4])
        effective_to = (
            parse_datetime(plan[5]) if plan[5] else None
        )

        if effective_from <= used_dt and (
            effective_to is None or used_dt <= effective_to
        ):
            applicable_plans.append(plan)

    if not applicable_plans:
        raise ValueError("No active calibration plan applies to this use date.")

    plan = max(applicable_plans, key=lambda p: parse_datetime(p[4]))

    interval_days = int(plan[1])
    policy_block = convert_policy(plan[2])
    grace_days = int(plan[3])

    # Find the latest successful, closed calibration before the use
    cursor.execute("""
        SELECT performed_at
        FROM CalibrationEvent
        WHERE asset_id = ?
        AND result = 'Pass'
        AND event_state = 'Closed'
    """, (asset_id,))

    events = cursor.fetchall()

    valid_events = []

    for event in events:
        event_dt = parse_datetime(event[0])

        if event_dt <= used_dt:
            valid_events.append(event_dt)

    if not valid_events:
        raise ValueError(
            "No successful closed calibration exists before this use date."
        )

    latest_calibration = max(valid_events)

    # Calculate due date and grace-period end
    due_dt = latest_calibration + timedelta(days=interval_days)
    grace_end = due_dt + timedelta(days=grace_days)

    outside_window = used_dt > due_dt
    beyond_grace = used_dt > grace_end

    # Check for an approved exception valid at the time of use
    cursor.execute("""
        SELECT requested_at, approved_by, approved_at,
            extension_due_at, status
        FROM Exception
        WHERE asset_id = ?
        AND status = 'Approved'
    """, (asset_id,))

    exceptions = cursor.fetchall()
    approved_extension = False

    for exception in exceptions:
        requested_at, approved_by, approved_at, extension_due_at, status = exception

        if not approved_by or not approved_at:
            continue

        requested_dt = parse_datetime(requested_at)
        approved_dt = parse_datetime(approved_at)
        extension_dt = parse_datetime(extension_due_at)

        if (
            requested_dt <= used_dt
            and approved_dt <= used_dt
            and used_dt <= extension_dt
        ):
            approved_extension = True
            break

    # Calculate the final decision
    if policy_block and beyond_grace and not approved_extension:
        decision = "Blocked"
    else:
        decision = "Allowed"

    return due_dt.isoformat(), policy_block, decision, outside_window

def generate_production_use_id(cursor, asset_id, used_at):
    from datetime import datetime

    used_datetime = datetime.fromisoformat(
        used_at.replace("Z", "+00:00")
    )

    timestamp = used_datetime.strftime("%Y%m%dT%H%M%S")

    prefix = f"USE-{asset_id}-{timestamp}-"

    cursor.execute("""
        SELECT production_use_id
        FROM ProductionUse
        WHERE production_use_id LIKE ?
    """, (prefix + "%",))

    existing_ids = cursor.fetchall()

    numbers = []

    for row in existing_ids:
        try:
            numbers.append(int(row[0].rsplit("-", 1)[-1]))
        except ValueError:
            continue

    next_number = max(numbers, default=0) + 1

    return f"{prefix}{next_number:06d}"

def create_production_use():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        asset_id = input("Enter Asset ID: ").strip()

        cursor.execute("""
            SELECT 1 FROM Asset WHERE asset_id = ?
        """, (asset_id,))

        if cursor.fetchone() is None:
            print("Invalid Asset ID.")
            return

        used_at = input("Enter Used Date (YYYY-MM-DD): ").strip()

        if not validate_date(used_at):
            print("Invalid Used Date.")
            return

        production_order_id = input(
            "Enter Production Order ID: "
        ).strip()

        operation = input("Enter Operation: ").strip()

        if not production_order_id or not operation:
            print("All required fields must be entered.")
            return

        # Automatically calculate calibration information
        try:
            (
                calibration_due_at,
                policy_block_overdue,
                use_decision,
                outside_window
            ) = get_production_use_rules(cursor, asset_id, used_at)

        except ValueError as error:
            print("Cannot create Production Use record:", error)
            return

        production_use_id = generate_production_use_id(
            cursor, asset_id, used_at
        )

        cursor.execute("""
            INSERT INTO ProductionUse (
                production_use_id,
                asset_id,
                used_at,
                production_order_id,
                operation,
                calibration_due_at,
                policy_block_overdue,
                use_decision,
                outside_valid_calibration_window
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            production_use_id,
            asset_id,
            used_at,
            production_order_id,
            operation,
            calibration_due_at,
            int(policy_block_overdue),
            use_decision,
            int(outside_window)
        ))

        conn.commit()

        print("\nPRODUCTION USE DECISION")
        print("-" * 50)
        print("Production Use ID:", production_use_id)
        print("Asset ID:", asset_id)
        print("Calibration Due Date:", calibration_due_at)
        print("Overdue Blocking Policy:", policy_block_overdue)
        print("Outside Calibration Window:", outside_window)
        print("Use Decision:", use_decision)
        print("\nProduction Use record created successfully!")

    except sqlite3.IntegrityError as error:
        conn.rollback()
        print("Database error:", error)

    except sqlite3.Error as error:
        conn.rollback()
        print("Database error:", error)

    finally:
        conn.close()
        
def main():
    while True:
        print("\n===== PRODUCTION USE MANAGEMENT =====")
        print("1. Display First 10 Production Use Records")
        print("2. Search by Production Use ID")
        print("3. Search by Asset ID")
        print("4. Search by Production Order ID")
        print("5. Display Records by Use Decision")
        print("6. Create New Production Use Record")
        print("7. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            display_production_use()

        elif choice == "2":
            search_by_production_use_id()

        elif choice == "3":
            search_by_asset_id()

        elif choice == "4":
            search_by_production_order_id()

        elif choice == "5":
            display_by_decision()

        elif choice == "6":
            create_production_use()

        elif choice == "7":
            print("Exiting Production Use Management.")
            break

        else:
            print("Invalid choice. Please enter 1 to 7.")


if __name__ == "__main__":
    main()
