
import instrument_management
import calibration_management
import work_order_management
import calibration_event_management
import certificate_management
import production_use_management
import exception_management
import alert_management
import audit_record_management
import corrective_action_management


def main():
    while True:
        print("\n==============================================")
        print("       CALIBRATION MANAGEMENT SYSTEM")
        print("==============================================")
        print("1. Instrument Management")
        print("2. Calibration Management")
        print("3. Work Order Management")
        print("4. Calibration Event Management")
        print("5. Certificate Management")
        print("6. Production Use Management")
        print("7. Exception Management")
        print("8. Alert Management")
        print("9. Audit Record Management")
        print("10. Corrective Action Management")
        print("0. Exit")
        print("==============================================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            instrument_management.main()
        elif choice == "2":
            calibration_management.main()
        elif choice == "3":
            work_order_management.main()
        elif choice == "4":
            calibration_event_management.main()
        elif choice == "5":
            certificate_management.main()
        elif choice == "6":
            production_use_management.main()
        elif choice == "7":
            exception_management.main()
        elif choice == "8":
            alert_management.main()
        elif choice == "9":
            audit_record_management.main()
        elif choice == "10":
            corrective_action_management.main()
        elif choice == "0":
            print("Exiting Calibration Management System.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
