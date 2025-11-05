from modules.database import get_all_users, update_user_status, get_user_profile, get_all_feedback, mark_feedback_resolved, get_account_lock_requests, unlock_user_account
from modules.activity_logger import view_logs, log_action, get_logs_dataframe, get_user_activity_summary, get_activity_statistics, display_logs_table
import pandas as pd
import numpy as np

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def print_separator(char="=", length=100):
    print(char * length)

def print_header(title):
    print()
    print_separator("=")
    print(f"  {title.upper()}")
    print_separator("=")
    print()

def admin_login():
    username = input("  Admin Username: ").strip()
    password = input("  Admin Password: ").strip()
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        print("\n  ✓ Authentication successful")
        print(f"  Welcome, Administrator {username}")
        log_action("Admin", "Logged in")
        input("\n  Press Enter to continue...")
        admin_menu()
    else:
        print("\n  ✗ Invalid admin credentials")
        input("\n  Press Enter to continue...")

def process_audit_requests():
    print_header("PROCESS AUDIT REQUESTS")
    
    from modules.database import get_audit_requests, mark_audit_completed
    
    requests = get_audit_requests()
    
    if not requests:
        print("  No pending audit requests.")
        return
    
    df = pd.DataFrame(requests, columns=['ID', 'Username', 'Timestamp', 'Status'])
    
    print_separator("-")
    print(f"  {'ID':<6} {'USERNAME':<20} {'TIMESTAMP':<20} {'STATUS':<12}")
    print_separator("-")
    
    for _, row in df.iterrows():
        print(f"  {row['ID']:<6} {row['Username']:<20} {row['Timestamp']:<20} {row['Status']:<12}")
    
    print_separator("-")
    
    audit_id = input("\n  Enter Audit Request ID to process (or 0 to cancel): ").strip()
    
    if audit_id == "0":
        return
    
    username = df[df['ID'] == int(audit_id)]['Username'].values[0]
    
    summary = get_user_activity_summary(username)
    
    if summary:
        print(f"\n  AUDIT REPORT FOR: {username}")
        print_separator("=")
        print(f"  Total Actions: {summary['total_actions']}")
        print(f"  Login Count: {summary['login_count']}")
        print(f"  Last Action: {summary['last_action']}")
        print(f"  Last Seen: {summary['last_seen']}")
        print("\n  ACTIONS BREAKDOWN:")
        print_separator("-")
        
        for action, count in summary['actions_breakdown'].items():
            print(f"  {action:<50}: {count}")
        
        print_separator("=")
        
        mark_audit_completed(int(audit_id))
        
        from modules.activity_logger import log_action
        log_action("Admin", f"Completed audit for {username} (Request ID: {audit_id})")
        log_action(username, f"Account audit completed by Admin - Summary: {summary['total_actions']} total actions, {summary['login_count']} logins")
        
        print("\n  ✓ Audit completed and logged for user")
    else:
        print("\n  No activity data available for this user")


def display_users_table(users_data):
    if not users_data:
        print("  No users found.")
        return
    
    df = pd.DataFrame(users_data, columns=['ID', 'Username', 'Status', 'Name', 'Email'])
    
    print_separator("-")
    print(f"  {'ID':<8} {'USERNAME':<20} {'STATUS':<15} {'NAME':<20} {'EMAIL':<30}")
    print_separator("-")
    
    for _, row in df.iterrows():
        name = row['Name'] if row['Name'] else 'N/A'
        email = row['Email'] if row['Email'] else 'N/A'
        print(f"  {row['ID']:<8} {row['Username']:<20} {row['Status']:<15} {name:<20} {email:<30}")
    
    print_separator("-")
    print(f"\n  Total Users: {len(df)}")

def view_all_users():
    print_header("ALL REGISTERED USERS")
    users = get_all_users()
    
    if not users:
        print("  No users in the system.")
        return
    
    display_users_table(users)
    
    df = pd.DataFrame(users, columns=['ID', 'Username', 'Status', 'Name', 'Email'])
    status_counts = df['Status'].value_counts().to_dict()
    
    print("\n  STATUS BREAKDOWN:")
    print_separator("-")
    for status, count in status_counts.items():
        print(f"  {status:<15}: {count}")
    print_separator("-")

def approve_reject_users():
    print_header("APPROVE / REJECT USERS")
    users = get_all_users()
    pending = [u for u in users if u[2] == "Pending"]
    
    if not pending:
        print("  No pending users for approval.")
        return
    
    print("  PENDING USERS:")
    print_separator("-")
    
    for u in pending:
        print(f"  ID: {u[0]} | Username: {u[1]} | Status: {u[2]}")
        profile = get_user_profile(u[0])
        if profile:
            print(f"    Name: {profile[0] or 'N/A'}")
            print(f"    Email: {profile[1] or 'N/A'}")
            print(f"    Purpose: {profile[2] or 'N/A'}")
            print(f"    Organization: {profile[3] or 'N/A'}")
        print_separator("-")
    
    uid = input("\n  Enter User ID to approve/reject (or 0 to cancel): ").strip()
    
    if uid == "0":
        return
    
    action = input("  [A] Approve / [R] Reject: ").strip().upper()
    
    if action == "A":
        update_user_status(int(uid), "Approved")
        print("\n  ✓ User approved successfully")
        log_action("Admin", f"Approved user ID {uid}")
    elif action == "R":
        update_user_status(int(uid), "Rejected")
        print("\n  ✓ User rejected")
        log_action("Admin", f"Rejected user ID {uid}")
    else:
        print("\n  ✗ Invalid action")

def suspend_unsuspend_users():
    print_header("SUSPEND / UNSUSPEND USERS")
    users = get_all_users()
    active = [u for u in users if u[2] in ["Approved", "Suspended"]]
    
    if not active:
        print("  No active users.")
        return
    
    print("  ACTIVE USERS:")
    print_separator("-")
    for u in active:
        print(f"  {u[0]}. {u[1]:<25} → {u[2]}")
    print_separator("-")
    
    uid = input("\n  Enter User ID to toggle suspend (or 0 to cancel): ").strip()
    
    if uid == "0":
        return
    
    status = [u[2] for u in active if str(u[0]) == uid]
    if status:
        new_status = "Suspended" if status[0] == "Approved" else "Approved"
        update_user_status(int(uid), new_status)
        print(f"\n  ✓ User status changed to: {new_status}")
        log_action("Admin", f"Changed user ID {uid} status to {new_status}")
    else:
        print("\n  ✗ Invalid User ID")

def view_activity_logs():
    print_header("ACTIVITY LOGS")
    
    print("  [1] View All Logs")
    print("  [2] View Recent Logs (Last 20)")
    print("  [3] View Statistics")
    print("  [4] Back")
    print()
    print_separator("-")
    
    choice = input("\n  Choose: ").strip()
    
    if choice == "1":
        print(display_logs_table())
        log_action("Admin", "Viewed all activity logs")
    elif choice == "2":
        print(display_logs_table(limit=20))
        log_action("Admin", "Viewed recent activity logs")
    elif choice == "3":
        stats = get_activity_statistics()
        if stats:
            print("\n  ACTIVITY STATISTICS:")
            print_separator("-")
            print(f"  Total Logs: {stats['total_logs']}")
            print(f"  Unique Users: {stats['unique_users']}")
            print(f"  Most Active User: {stats['most_active_user']}")
            print("\n  ACTIONS PER USER:")
            print_separator("-")
            for user, count in stats['actions_per_user'].items():
                print(f"  {user:<20}: {count} actions")
            print_separator("-")
        else:
            print("\n  No statistics available.")
        log_action("Admin", "Viewed activity statistics")

def view_user_activity_summary():
    print_header("USER ACTIVITY SUMMARY")
    
    username = input("  Enter username to view summary: ").strip()
    summary = get_user_activity_summary(username)
    
    if not summary:
        print(f"\n  No activity found for user: {username}")
        return
    
    print(f"\n  ACTIVITY SUMMARY FOR: {username}")
    print_separator("-")
    print(f"  Total Actions: {summary['total_actions']}")
    print(f"  Login Count: {summary['login_count']}")
    print(f"  Last Action: {summary['last_action']}")
    print(f"  Last Seen: {summary['last_seen']}")
    print("\n  ACTIONS BREAKDOWN:")
    print_separator("-")
    
    for action, count in summary['actions_breakdown'].items():
        print(f"  {action:<50}: {count}")
    
    print_separator("-")
    log_action("Admin", f"Viewed activity summary for {username}")

def view_feedback():
    print_header("USER FEEDBACK")
    
    feedback_list = get_all_feedback()
    
    if not feedback_list:
        print("  No feedback submitted yet.")
        return
    
    df = pd.DataFrame(feedback_list, columns=['ID', 'Username', 'Feedback', 'Timestamp', 'Status'])
    
    print_separator("-")
    print(f"  {'ID':<6} {'USERNAME':<20} {'STATUS':<12} {'TIMESTAMP':<20}")
    print_separator("-")
    
    for _, row in df.iterrows():
        print(f"  {row['ID']:<6} {row['Username']:<20} {row['Status']:<12} {row['Timestamp']:<20}")
        print(f"  Feedback: {row['Feedback']}")
        print_separator("-")
    
    print(f"\n  Total Feedback: {len(df)}")
    print(f"  Pending: {len(df[df['Status'] == 'Pending'])}")
    print(f"  Resolved: {len(df[df['Status'] == 'Resolved'])}")
    
    fid = input("\n  Enter Feedback ID to mark as resolved (or 0 to skip): ").strip()
    
    if fid != "0":
        mark_feedback_resolved(int(fid))
        print("\n  ✓ Feedback marked as resolved")
        log_action("Admin", f"Resolved feedback ID {fid}")

def view_unlock_requests():
    print_header("ACCOUNT UNLOCK REQUESTS")
    
    requests = get_account_lock_requests()
    
    if not requests:
        print("  No unlock requests pending.")
        return
    
    df = pd.DataFrame(requests, columns=['ID', 'Username', 'Reason', 'Timestamp'])
    
    print_separator("-")
    print(f"  {'ID':<6} {'USERNAME':<20} {'TIMESTAMP':<20}")
    print_separator("-")
    
    for _, row in df.iterrows():
        print(f"  {row['ID']:<6} {row['Username']:<20} {row['Timestamp']:<20}")
        print(f"  Reason: {row['Reason']}")
        print_separator("-")
    
    uid = input("\n  Enter Request ID to unlock account (or 0 to cancel): ").strip()
    
    if uid != "0":
        unlock_user_account(int(uid))
        print("\n  ✓ Account unlocked successfully")
        log_action("Admin", f"Unlocked account for request ID {uid}")

def admin_menu():
    while True:
        print_header("ADMIN PORTAL")
        print("  [1]  View All Users")
        print("  [2]  Approve / Reject Users")
        print("  [3]  Suspend / Unsuspend Users")
        print("  [4]  View Activity Logs")
        print("  [5]  View User Activity Summary")
        print("  [6]  View User Feedback")
        print("  [7]  View Unlock Requests")
        print("  [8]  Process Audit Requests")
        print("  [9]  Logout")
        print()
        print_separator("-")
        
        choice = input("\n  Choose: ").strip()
        
        if choice == "1":
            view_all_users()
        elif choice == "2":
            approve_reject_users()
        elif choice == "3":
            suspend_unsuspend_users()
        elif choice == "4":
            view_activity_logs()
        elif choice == "5":
            view_user_activity_summary()
        elif choice == "6":
            view_feedback()
        elif choice == "7":
            view_unlock_requests()
        elif choice == "8":
            process_audit_requests()
        elif choice == "9":
            log_action("Admin", "Logged out")
            print("\n  ✓ Logged out successfully")
            input("\n  Press Enter to continue...")
            break
        else:
            print("\n  ✗ Invalid choice")
        
        input("\n  Press Enter to continue...")
