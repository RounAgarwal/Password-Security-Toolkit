import sys
import pandas as pd
import numpy as np
from modules.database import (add_user, get_user, get_user_by_name, add_password, 
                               get_passwords, get_passwords_dataframe, update_password, 
                               delete_password, add_feedback, lock_user_account, 
                               request_account_unlock, add_audit_request)
from modules.security_utils import (generate_password, check_strength, analyze_password_entropy,
                                     compare_passwords, generate_multiple_passwords, 
                                     validate_password_requirements)
from modules.activity_logger import log_action
from modules.database import get_user_completed_audits
from modules.activity_logger import get_user_activity_summary, get_logs_dataframe



def print_separator(char="=", length=100):
    print(char * length)

def print_header(title):
    print()
    print_separator("=")
    print(f"  {title.upper()}")
    print_separator("=")
    print()

def register():
    print_header("USER REGISTRATION")
    
    print("  Please provide the following details:")
    print_separator("-")
    
    username = input("  Username: ").strip()
    if get_user_by_name(username):
        print("\n  ✗ Username already exists")
        input("\n  Press Enter to continue...")
        return
    
    password = input("  Password: ").strip()
    
    strength = check_strength(password)
    print(f"\n  Password Strength: {strength['color']} {strength['strength']} ({strength['score']}/5)")
    
    if strength['score'] < 3:
        print("  ⚠ Warning: Weak password detected!")
        print("  Suggestions:")
        for suggestion in strength['feedback']:
            print(f"    • {suggestion}")
        
        confirm = input("\n  Continue with this password? [Y/N]: ").strip().upper()
        if confirm != "Y":
            print("\n  Registration cancelled")
            input("\n  Press Enter to continue...")
            return
    
    print_separator("-")
    print("\n  ADDITIONAL INFORMATION (Optional)")
    print_separator("-")
    
    name = input("  Full Name: ").strip() or None
    email = input("  Email Address: ").strip() or None
    purpose = input("  Purpose of Use: ").strip() or None
    organization = input("  Organization: ").strip() or None
    
    if add_user(username, password, name, email, purpose, organization):
        print("\n  ✓ Registration successful!")
        print("  ⏳ Your account is pending admin approval")
        print("  You will be able to login once approved")
        log_action(username, "Registered - Pending approval")
    else:
        print("\n  ✗ Registration failed")
    
    input("\n  Press Enter to continue...")

def login():
    username = input("  Username: ").strip()
    password = input("  Password: ").strip()
    
    user = get_user(username, password)
    
    if not user:
        print("\n  ✗ Invalid credentials")
        input("\n  Press Enter to continue...")
        return None
    
    if user[3] == "Locked":
        print("\n  ⚠ Your account is locked")
        print("  You can request an unlock from the admin")
        
        request_unlock = input("\n  Request unlock? [Y/N]: ").strip().upper()
        if request_unlock == "Y":
            reason = input("  Reason for unlock request: ").strip()
            request_account_unlock(user[0], username, reason)
            print("\n  ✓ Unlock request submitted")
            log_action(username, "Requested account unlock")
        
        input("\n  Press Enter to continue...")
        return None
    
    if user[3] != "Approved":
        print(f"\n  ⚠ Account status: {user[3]}")
        print("  Please wait for admin approval")
        input("\n  Press Enter to continue...")
        return None
    
    print(f"\n  ✓ Login successful")
    print(f"  Welcome back, {username}!")
    log_action(username, "Logged in")
    input("\n  Press Enter to continue...")
    user_menu(user[0], username)

def display_passwords_table(passwords_df):
    if passwords_df.empty:
        print("  No passwords saved yet")
        return
    
    print_separator("-")
    print(f"  {'ID':<8} {'LABEL':<30} {'PASSWORD':<40}")
    print_separator("-")
    
    for _, row in passwords_df.iterrows():
        masked_pwd = '*' * 8 + row['Password'][-4:] if len(row['Password']) > 4 else '*' * len(row['Password'])
        print(f"  {row['ID']:<8} {row['Label']:<30} {masked_pwd:<40}")
    
    print_separator("-")
    print(f"\n  Total Passwords Stored: {len(passwords_df)}")

def add_password_menu(user_id, username):
    print_header("ADD NEW PASSWORD")
    
    label = input("  Label/Website: ").strip()
    
    print("\n  [1] Enter password manually")
    print("  [2] Generate strong password")
    print_separator("-")
    
    choice = input("\n  Choose: ").strip()
    
    if choice == "1":
        pwd = input("\n  Password: ").strip()
    elif choice == "2":
        print("\n  PASSWORD GENERATOR OPTIONS:")
        print_separator("-")
        
        length = input("  Length (default 12): ").strip()
        length = int(length) if length.isdigit() else 12
        
        pwd = generate_password(length)
        print(f"\n  Generated Password: {pwd}")
        
        strength = check_strength(pwd)
        print(f"  Strength: {strength['color']} {strength['strength']} ({strength['score']}/5)")
        print(f"  Entropy: {analyze_password_entropy(pwd)} bits")
    else:
        print("\n  ✗ Invalid choice")
        return
    
    add_password(user_id, label, pwd)
    print("\n  ✓ Password saved successfully")
    log_action(username, f"Added password for {label}")

def view_passwords_menu(user_id, username):
    print_header("SAVED PASSWORDS")
    
    passwords_df = get_passwords_dataframe(user_id)
    
    if passwords_df.empty:
        print("  No passwords saved yet")
        log_action(username, "Viewed saved passwords (empty)")
        return
    
    display_passwords_table(passwords_df)
    
    show_full = input("\n  Show full passwords? [Y/N]: ").strip().upper()
    
    if show_full == "Y":
        print_separator("-")
        print(f"  {'ID':<8} {'LABEL':<30} {'PASSWORD':<40}")
        print_separator("-")
        
        for _, row in passwords_df.iterrows():
            print(f"  {row['ID']:<8} {row['Label']:<30} {row['Password']:<40}")
        
        print_separator("-")
    
    log_action(username, "Viewed saved passwords")

def update_password_menu(user_id, username):
    print_header("UPDATE PASSWORD")
    
    passwords_df = get_passwords_dataframe(user_id)
    
    if passwords_df.empty:
        print("  No passwords to update")
        return
    
    display_passwords_table(passwords_df)
    
    rid = input("\n  Enter ID to update (or 0 to cancel): ").strip()
    
    if rid == "0":
        return
    
    if not rid.isdigit() or int(rid) not in passwords_df['ID'].values:
        print("\n  ✗ Invalid ID")
        return
    
    new_pwd = input("  Enter new password: ").strip()
    
    strength = check_strength(new_pwd)
    print(f"\n  Password Strength: {strength['color']} {strength['strength']} ({strength['score']}/5)")
    
    confirm = input("\n  Confirm update? [Y/N]: ").strip().upper()
    
    if confirm == "Y":
        update_password(int(rid), new_pwd)
        print("\n  ✓ Password updated successfully")
        log_action(username, f"Updated password ID {rid}")
    else:
        print("\n  Update cancelled")

def delete_password_menu(user_id, username):
    print_header("DELETE PASSWORD")
    
    passwords_df = get_passwords_dataframe(user_id)
    
    if passwords_df.empty:
        print("  No passwords to delete")
        return
    
    display_passwords_table(passwords_df)
    
    rid = input("\n  Enter ID to delete (or 0 to cancel): ").strip()
    
    if rid == "0":
        return
    
    if not rid.isdigit() or int(rid) not in passwords_df['ID'].values:
        print("\n  ✗ Invalid ID")
        return
    
    confirm = input("\n  ⚠ Confirm deletion? [Y/N]: ").strip().upper()
    
    if confirm == "Y":
        delete_password(int(rid))
        print("\n  ✓ Password deleted successfully")
        log_action(username, f"Deleted password ID {rid}")
    else:
        print("\n  Deletion cancelled")

def generate_password_menu(username):
    print_header("PASSWORD GENERATOR")
    
    print("  [1] Generate single password")
    print("  [2] Generate multiple passwords")
    print("  [3] Custom generation options")
    print_separator("-")
    
    choice = input("\n  Choose: ").strip()
    
    if choice == "1":
        pwd = generate_password()
        strength = check_strength(pwd)
        entropy = analyze_password_entropy(pwd)
        
        print(f"\n  Generated Password: {pwd}")
        print(f"  Strength: {strength['color']} {strength['strength']} ({strength['score']}/5)")
        print(f"  Entropy: {entropy} bits")
        
        log_action(username, "Generated single password")
        
    elif choice == "2":
        count = input("\n  How many passwords to generate? (default 5): ").strip()
        count = int(count) if count.isdigit() else 5
        
        length = input("  Length (default 12): ").strip()
        length = int(length) if length.isdigit() else 12
        
        passwords = generate_multiple_passwords(count, length)
        
        print("\n  GENERATED PASSWORDS:")
        print_separator("-")
        print(f"  {'PASSWORD':<30} {'STRENGTH':<15} {'ENTROPY (bits)':<15}")
        print_separator("-")
        
        for pwd_info in passwords:
            print(f"  {pwd_info['password']:<30} {pwd_info['strength']:<15} {pwd_info['entropy']:<15}")
        
        print_separator("-")
        log_action(username, f"Generated {count} passwords")
        
    elif choice == "3":
        length = input("\n  Length (default 12): ").strip()
        length = int(length) if length.isdigit() else 12
        
        use_upper = input("  Include uppercase? [Y/N] (default Y): ").strip().upper() != "N"
        use_lower = input("  Include lowercase? [Y/N] (default Y): ").strip().upper() != "N"
        use_numbers = input("  Include numbers? [Y/N] (default Y): ").strip().upper() != "N"
        use_special = input("  Include special chars? [Y/N] (default Y): ").strip().upper() != "N"
        
        pwd = generate_password(length, use_special, use_numbers, use_upper, use_lower)
        strength = check_strength(pwd)
        entropy = analyze_password_entropy(pwd)
        
        print(f"\n  Generated Password: {pwd}")
        print(f"  Strength: {strength['color']} {strength['strength']} ({strength['score']}/5)")
        print(f"  Entropy: {entropy} bits")
        
        log_action(username, "Generated custom password")

def check_password_strength_menu(username):
    print_header("PASSWORD STRENGTH CHECKER")
    
    print("  [1] Check single password")
    print("  [2] Compare two passwords")
    print_separator("-")
    
    choice = input("\n  Choose: ").strip()
    
    if choice == "1":
        pwd = input("\n  Enter password to analyze: ").strip()
        
        strength = check_strength(pwd)
        entropy = analyze_password_entropy(pwd)
        
        print(f"\n  PASSWORD ANALYSIS:")
        print_separator("-")
        print(f"  Strength: {strength['color']} {strength['strength']}")
        print(f"  Score: {strength['score']}/5 ({strength['percentage']:.0f}%)")
        print(f"  Entropy: {entropy} bits")
        
        if strength['feedback']:
            print("\n  SUGGESTIONS FOR IMPROVEMENT:")
            for suggestion in strength['feedback']:
                print(f"    • {suggestion}")
        
        print_separator("-")
        log_action(username, "Checked password strength")
        
    elif choice == "2":
        pwd1 = input("\n  Enter first password: ").strip()
        pwd2 = input("  Enter second password: ").strip()
        
        comparison = compare_passwords(pwd1, pwd2)
        
        print(f"\n  PASSWORD COMPARISON:")
        print_separator("-")
        print(f"  Password 1:")
        print(f"    Strength: {comparison['password1']['strength']}")
        print(f"    Score: {comparison['password1']['score']}/5")
        print(f"    Entropy: {comparison['password1']['entropy']} bits")
        print()
        print(f"  Password 2:")
        print(f"    Strength: {comparison['password2']['strength']}")
        print(f"    Score: {comparison['password2']['score']}/5")
        print(f"    Entropy: {comparison['password2']['entropy']} bits")
        print()
        print(f"  Recommendation: {comparison['recommendation']} is stronger")
        print_separator("-")
        
        log_action(username, "Compared two passwords")

def submit_feedback_menu(user_id, username):
    print_header("SUBMIT FEEDBACK")
    
    feedback = input("  Your feedback/suggestion: ").strip()
    
    if not feedback:
        print("\n  Feedback cannot be empty")
        return
    
    add_feedback(user_id, username, feedback)
    print("\n  ✓ Feedback submitted successfully")
    print("  Thank you for your feedback!")
    log_action(username, "Submitted feedback")

def lock_account_menu(user_id, username):
    print_header("LOCK ACCOUNT")
    
    print("  ⚠ WARNING: This will lock your account")
    print("  You will need to request admin to unlock it")
    print_separator("-")
    
    confirm = input("\n  Are you sure? [Y/N]: ").strip().upper()
    
    if confirm != "Y":
        print("\n  Action cancelled")
        return
    
    reason = input("\n  Reason for locking (optional): ").strip()
    reason = reason if reason else "User requested lock"
    
    lock_user_account(user_id, username, reason)
    print("\n  ✓ Account locked successfully")
    print("  You can request unlock from login screen")
    log_action(username, "Locked own account")
    input("\n  Press Enter to continue...")
    sys.exit(0)

def request_audit_menu(user_id, username):
    print_header("REQUEST ACCOUNT AUDIT")
    
    print("  An audit will review:")
    print("    • Your account activity logs")
    print("    • Login history")
    print("    • Password operations")
    print("    • Security events")
    print_separator("-")
    
    confirm = input("\n  Submit audit request? [Y/N]: ").strip().upper()
    
    if confirm == "Y":
        add_audit_request(user_id, username)
        print("\n  ✓ Audit request submitted")
        print("  Admin will review and provide summary")
        log_action(username, "Requested account audit")
    else:
        print("\n  Request cancelled")

def view_my_audit_summary(user_id, username):
    print_header("MY COMPLETED AUDITS")
    completed = get_user_completed_audits(user_id)
    
    if not completed:
        print("  No completed audits yet.")
        return

    print_separator("-")
    print(f"  {'ID':<6} {'TIMESTAMP':<20} {'STATUS':<12}")
    print_separator("-")
    for a in completed:
        print(f"  {a[0]:<6} {a[2]:<20} {a[3]:<12}")
    print_separator("-")

    choice = input("\n  Enter Audit ID to view report (or 0 to cancel): ").strip()
    if choice == "0":
        return

    audit_id = int(choice)
    df = get_logs_dataframe()
    user_logs = df[df['Username'] == username]
    log_row = user_logs[user_logs['Action'].str.contains(f"Account audit completed by Admin", case=False, na=False)]
    if log_row.empty:
        print("\n  No detailed report found for this audit.")
        return

    summary = get_user_activity_summary(username)

    print_header(f"AUDIT REPORT FOR {username}")
    print(f"  Total Actions: {summary['total_actions']}")
    print(f"  Login Count: {summary['login_count']}")
    print(f"  Last Action: {summary['last_action']}")
    print(f"  Last Seen: {summary['last_seen']}")
    print("\n  ACTIONS BREAKDOWN:")
    print_separator("-")
    for action, count in summary['actions_breakdown'].items():
        print(f"  {action:<50}: {count}")
    print_separator("=")

    print("\n  NOTE: This audit data is live, generated from your latest activity logs.")
    log_action(username, f"Viewed completed audit ID {audit_id}")


def view_audit_reports_menu(user_id, username):
    print_header("MY AUDIT REPORTS")

    from modules.database import get_user_audit_requests
    audits = get_user_audit_requests(user_id)

    if not audits:
        print("  No audit requests found.")
        return

    print_separator("-")
    print(f"  {'ID':<6} {'TIMESTAMP':<20} {'STATUS':<12}")
    print_separator("-")

    for audit in audits:
        print(f"  {audit[0]:<6} {audit[1]:<20} {audit[2]:<12}")
    print_separator("-")
    
    from modules.activity_logger import get_logs_dataframe
    df = get_logs_dataframe()
    user_logs = df[(df['Username'] == username) & (df['Action'].str.contains("Account audit completed", case=False))]
    
    if not user_logs.empty:
        print("\n  COMPLETED AUDITS SUMMARY:")
        print_separator("-")
        for _, row in user_logs.iterrows():
            print(f"  {row['Timestamp']}: {row['Action']}")
        print_separator("-")
    else:
        print("\n  No completed audit summaries yet.")
    
    log_action(username, "Viewed audit reports")

    

def user_menu(user_id, username):
    while True:
        print_header("USER PORTAL")
        print(f"  Logged in as: {username}")
        print_separator("-")
        print("\n  PASSWORD MANAGEMENT")
        print("    [1]  Add Password")
        print("    [2]  View Passwords")
        print("    [3]  Update Password")
        print("    [4]  Delete Password")
        print("\n  PASSWORD TOOLS")
        print("    [5]  Generate Strong Password")
        print("    [6]  Check Password Strength")
        print("\n  ACCOUNT OPTIONS")
        print("    [7]  Submit Feedback")
        print("    [8]  Request Account Audit")
        print("    [9]  View My Audit Reports")
        print("    [10] Lock Account")
        print("    [11] Logout")
        print()
        print_separator("-")
        
        choice = input("\n  Choose: ").strip()
        
        if choice == "1":
            add_password_menu(user_id, username)
        elif choice == "2":
            view_passwords_menu(user_id, username)
        elif choice == "3":
            update_password_menu(user_id, username)
        elif choice == "4":
            delete_password_menu(user_id, username)
        elif choice == "5":
            generate_password_menu(username)
        elif choice == "6":
            check_password_strength_menu(username)
        elif choice == "7":
            submit_feedback_menu(user_id, username)
        elif choice == "8":
            request_audit_menu(user_id, username)
        elif choice == "9":
            view_my_audit_summary(user_id, username)
        elif choice == "10":
            lock_account_menu(user_id, username)
        elif choice == "11":
            log_action(username, "Logged out")
            print("\n  ✓ Logged out successfully")
            input("\n  Press Enter to continue...")
            break
        else:
            print("\n  ✗ Invalid choice")
        
        input("\n  Press Enter to continue...")
