# Calibration Management System

## 1. Project Overview

The Calibration Management System is a Python and SQLite-based application designed to manage instrument calibration activities, schedule calibration, track certificates, and prevent the use of overdue instruments when policy requires.

## 2. Problem Statement

Organizations use measuring instruments that require periodic calibration to maintain accuracy and reliability. Missing calibration schedules or using overdue instruments can affect product quality and compliance.

This project provides a centralized system to manage calibration activities, maintain traceability, and control production use.

## 3. Project Objectives

- Maintain instrument records.
- Schedule and track calibration activities.
- Manage calibration work orders.
- Record calibration results.
- Manage calibration certificates.
- Detect overdue instruments.
- Block production use when required by policy.
- Manage calibration exceptions.
- Maintain alerts and audit records.
- Track corrective actions.

## 4. Technologies Used

- Python 3
- SQLite
- SQL
- Python sqlite3 library

## 5. Main Modules

1. Instrument Management
2. Calibration Management
3. Work Order Management
4. Calibration Event Management
5. Certificate Management
6. Production Use Management
7. Exception Management
8. Alert Management
9. Audit Record Management
10. Corrective Action Management

## 6. Project Structure

```text
Calibration_Management_System/
│
├── main.py
├── instrument_management.py
├── calibration_management.py
├── work_order_management.py
├── calibration_event_management.py
├── certificate_management.py
├── production_use_management.py
├── exception_management.py
├── alert_management.py
├── audit_record_management.py
├── corrective_action_management.py
├── check_overdue_assets.py
├── final_database_check.py
├── database/
│   └── calibration_management.db
├── .gitignore
└── README.md
```

## 7. Requirements

- Python 3 installed.
- SQLite support (included with Python).
- Git (optional, for cloning the repository).

No additional Python packages are required for the core application if it uses only Python standard-library modules.

## 8. How to Run

### Step 1: Clone the repository

```bash
git clone https://github.com/rohithreddy69/Calibration-Management-System.git
```

### Step 2: Open the project folder

```bash
cd Calibration-Management-System
```

### Step 3: Run the application

```bash
py main.py
```

### Step 4: Select a module

Use the main menu to access the ten management modules.

## 9. Database Information

The application uses SQLite.

Database file:

`database/calibration_management.db`

The database contains 12 tables for instrument information, calibration plans, work orders, calibration events, certificates, production use, exceptions, alerts, audits, and corrective actions, along with supporting reference tables.

## 10. Calibration and Production-Use Control

The system tracks calibration due dates and evaluates production-use requests.

When overdue-use blocking is enabled by policy, an overdue instrument can receive a Blocked decision.

Approved exceptions may be considered according to the configured exception rules.

## 11. Database Validation

Run the database validation script:

```bash
py final_database_check.py
```

The script checks:

- SQLite database integrity.
- Foreign-key constraints.
- Record counts across the database tables.

### Validation Results

- Database integrity: OK
- Foreign-key errors: 0
- Tables checked: 12
- Total records at final validation: 115,805

Record counts may change when new records are created.

## 12. Testing Performed

- Python syntax validation.
- Instrument management testing.
- Calibration management testing.
- Work order management testing.
- Calibration event management testing.
- Certificate management testing.
- Production-use management testing.
- Exception management testing.
- Alert management testing.
- Audit record management testing.
- Corrective action management testing.
- Database integrity and foreign-key validation.

## 13. Conclusion

The Calibration Management System provides an integrated solution for instrument calibration scheduling, certificate management, overdue monitoring, production-use control, exception handling, and audit traceability.

## 14. Author

Rohith Reddy
