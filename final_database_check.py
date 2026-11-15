import sqlite3

DB_PATH = "database/calibration_management.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\n===== FINAL DATABASE INTEGRITY CHECK =====")

# 1. Database integrity
result = cursor.execute("PRAGMA integrity_check").fetchone()
print("\nDatabase Integrity:", result[0])

# 2. Foreign key validation
foreign_key_errors = cursor.execute(
    "PRAGMA foreign_key_check"
).fetchall()

print("Foreign Key Errors:", len(foreign_key_errors))

if foreign_key_errors:
    for error in foreign_key_errors[:10]:
        print(error)

# 3. Table record counts
tables = [
    "InstrumentType",
    "Supplier",
    "Asset",
    "CalibrationPlan",
    "WorkOrder",
    "CalibrationEvent",
    "Certificate",
    "ProductionUse",
    "Exception",
    "CorrectiveAction",
    "Alert",
    "AuditRecord"
]

print("\n===== TABLE RECORD COUNTS =====")

for table in tables:
    count = cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"{table}: {count}")

conn.close()

print("\n===== CHECK COMPLETED =====")