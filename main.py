import os
from modules.database import initialize_database
from modules.admin_portal import admin_login
from modules.user_portal import register, login

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    while True:
        print("\n=== Password & Security Toolkit ===")
        print("1. User Login")
        print("2. Register")
        print("3. Admin Login")
        print("4. Exit")
        ch = input("Choose: ").strip()
        if ch == "1":
            login()
        elif ch == "2":
            register()
        elif ch == "3":
            admin_login()
        elif ch == "4":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    initialize_database()
    main_menu()
