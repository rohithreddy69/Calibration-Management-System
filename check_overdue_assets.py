import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("database/calibration_management.db")
cursor = conn.cursor()

query = """
SELECT
    p.asset_id,
    p.interval_days,
    e.performed_at
FROM CalibrationPlan p
JOIN CalibrationEvent e
    ON e.asset_id = p.asset_id
WHERE p.plan_state = 'Active'
AND p.policy_block_overdue = 'True'
AND e.result = 'Pass'
AND lower(e.event_state) = 'closed'
AND e.performed_at = (
    SELECT MAX(e2.performed_at)
    FROM CalibrationEvent e2
    WHERE e2.asset_id = p.asset_id
    AND e2.result = 'Pass'
    AND lower(e2.event_state) = 'closed'
    AND e2.performed_at <= '2026-11-15'
)
LIMIT 20
"""

rows = cursor.execute(query).fetchall()

print("\nOVERDUE ASSET CHECK")
print("-" * 60)

today = datetime(2026, 11, 15)

for asset_id, interval_days, performed_at in rows:
    calibration_date = datetime.fromisoformat(
        performed_at.replace("Z", "+00:00")
    ).replace(tzinfo=None)

    due_date = calibration_date + timedelta(days=interval_days)

    if due_date.date() < today.date():
        print(asset_id, "Due:", due_date.date(), "BLOCKING TEST CANDIDATE")

conn.close()