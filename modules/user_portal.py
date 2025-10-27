import sys
from modules.database import add_user, get_user, get_user_by_name, add_password, get_passwords, update_password, delete_password
from modules.security_utils import generate_password, check_strength
from modules.activity_logger import log_action

def register():
    username = input("Enter new username: ").strip()
    if get_user_by_name(username):
        print("Username already exists.")
        return
    password = input("Enter new password: ").strip()
    if add_user(username, password):
        print("Registration successful. Await admin approval.")
        log_action(username, "Registered - Pending approval")
    else:
        print("Registration failed.")

def login():
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    user = get_user(username, password)
    if not user:
        print("Invalid credentials.")
        return None
    if user[3] != "Approved":
        print("Account not approved by admin.")
        return None
    print(f"Welcome {username}!")
    log_action(username, "Logged in")
    user_menu(user[0], username)

def user_menu(user_id, username):
    while True:
        print("\n1. Add password")
        print("2. View passwords")
        print("3. Update password")
        print("4. Delete password")
        print("5. Generate strong password")
        print("6. Check password strength")
        print("7. Logout")
        ch = input("Choose: ").strip()
        if ch == "1":
            label = input("Label: ").strip()
            pwd = input("Password: ").strip()
            add_password(user_id, label, pwd)
            print("Password saved.")
            log_action(username, f"Added password for {label}")
        elif ch == "2":
            records = get_passwords(user_id)
            print("\nSaved Passwords:")
            for r in records:
                print(f"{r[0]}. {r[1]} → {r[2]}")
            log_action(username, "Viewed saved passwords")
        elif ch == "3":
            records = get_passwords(user_id)
            for r in records:
                print(f"{r[0]}. {r[1]}")
            rid = input("Enter ID to update: ").strip()
            new_pwd = input("Enter new password: ").strip()
            update_password(rid, new_pwd)
            print("Updated successfully.")
            log_action(username, f"Updated password ID {rid}")
        elif ch == "4":
            records = get_passwords(user_id)
            for r in records:
                print(f"{r[0]}. {r[1]}")
            rid = input("Enter ID to delete: ").strip()
            delete_password(rid)
            print("Deleted successfully.")
            log_action(username, f"Deleted password ID {rid}")
        elif ch == "5":
            pwd = generate_password()
            print(f"Generated: {pwd}")
            log_action(username, "Generated new password")
        elif ch == "6":
            pwd = input("Enter password: ").strip()
            print("Strength:", check_strength(pwd))
            log_action(username, "Checked password strength")
        elif ch == "7":
            log_action(username, "Logged out")
            break
        else:
            print("Invalid choice.")
