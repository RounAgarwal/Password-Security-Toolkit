from modules.database import get_all_users, update_user_status
from modules.activity_logger import view_logs, log_action

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def admin_login():
    username = input("Admin username: ").strip()
    password = input("Admin password: ").strip()
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        print("Welcome, Admin.")
        log_action("Admin", "Logged in")
        admin_menu()
    else:
        print("Invalid admin credentials.")

def admin_menu():
    while True:
        print("\n--- Admin Portal ---")
        print("1. View all users")
        print("2. Approve/Reject users")
        print("3. Suspend/Unsuspend users")
        print("4. View activity logs")
        print("5. Logout")
        ch = input("Choose: ").strip()
        if ch == "1":
            users = get_all_users()
            print(f"\n{'ID':<10} {'Username':<20} {'Status':<15}")
            print("-" * 50)
            for u in users:
                print(f"{u[0]:<10} {u[1]:<20} {u[2]:<15}")
        elif ch == "2":
            users = get_all_users()
            pending = [u for u in users if u[2] == "Pending"]
            if not pending:
                print("No pending users.")
            else:
                for u in pending:
                    print(f"{u[0]}. {u[1]} → {u[2]}")
                uid = input("Enter user ID to approve/reject: ").strip()
                act = input("Approve (A) / Reject (R): ").strip().upper()
                if act == "A":
                    update_user_status(int(uid), "Approved")
                    print("User approved.")
                    log_action("Admin", f"Approved user ID {uid}")
                elif act == "R":
                    update_user_status(int(uid), "Rejected")
                    print("User rejected.")
                    log_action("Admin", f"Rejected user ID {uid}")
        elif ch == "3":
            users = get_all_users()
            approved = [u for u in users if u[2] in ["Approved", "Suspended"]]
            if not approved:
                print("No active users.")
            else:
                for u in approved:
                    print(f"{u[0]}. {u[1]} → {u[2]}")
                uid = input("Enter user ID to toggle suspend: ").strip()
                status = [u[2] for u in approved if str(u[0]) == uid]
                if status:
                    new_status = "Suspended" if status[0] == "Approved" else "Approved"
                    update_user_status(int(uid), new_status)
                    print(f"User now {new_status}.")
                    log_action("Admin", f"Toggled suspend for user ID {uid}")
        elif ch == "4":
            print("\n--- Activity Logs ---")
            print(view_logs())
            log_action("Admin", "Viewed activity logs")
        elif ch == "5":
            log_action("Admin", "Logged out")
            break
        else:
            print("Invalid choice.")
