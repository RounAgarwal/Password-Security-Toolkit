"""
================================================================================
                    PASSWORD & SECURITY TOOLKIT
================================================================================
"""

import os
import sys
from modules.database import initialize_database
from modules.admin_portal import admin_login
from modules.user_portal import register, login
from modules.activity_logger import log_action

def clear_screen():
    """Clear the terminal screen based on operating system"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Display application banner"""
    clear_screen()
    print("=" * 80)
    print(" " * 20 + "\tPASSWORD & SECURITY TOOLKIT")
    print("=" * 80)
    print()

def print_separator(char="=", length=80):
    """Print a separator line"""
    print(char * length)

def print_section_header(title):
    """Print a formatted section header"""
    print()
    print_separator("=")
    print(f"  {title.upper()}")
    print_separator("=")

def display_main_menu():
    """Display the main menu options"""
    print_banner()
    print_section_header("MAIN MENU")
    print()
    print("  [1] User Login")
    print("  [2] Register New Account")
    print("  [3] Admin Portal")
    print("  [4] About")
    print("  [5] Exit Application")
    print()
    print_separator("-")

def show_about():
    """Display application information"""
    print_section_header("ABOUT THIS APPLICATION")
    print()
    print("  \tPassword & Security Toolkit")
    print("  A comprehensive password management system with:")
    print()
    print("  ✓ Secure password storage with encryption")
    print("  ✓ Admin approval workflow")
    print("  ✓ Password strength analysis")
    print("  ✓ Activity logging and auditing")
    print("  ✓ User profile management")
    print("  ✓ Feedback system")
    print()
    print_separator("-")
    input("\n  Press Enter to continue...")
    print()
    print()

def main_menu():
    """Main application loop"""
    while True:
        try:
            display_main_menu()
            choice = input("  Enter your choice [1-5]: ").strip()
            
            if choice == "1":
                print_section_header("USER LOGIN")
                login()
                
            elif choice == "2":
                register()
                
            elif choice == "3":
                print_section_header("ADMIN PORTAL")
                admin_login()
                
            elif choice == "4":
                show_about()
                
            elif choice == "5":
                print_section_header("GOODBYE")
                print("\n  Thank you for using Password & Security Toolkit!")
                print("  Exiting application...\n")
                print_separator("=")
                log_action("System", "Application shutdown")
                sys.exit(0)
                
            else:
                print("\n  ⚠ Invalid choice. Please select options 1-5.")
                input("\n  Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n  ⚠ Application interrupted by user.")
            print("  Exiting safely...\n")
            print_separator("=")
            sys.exit(0)
            
        except Exception as e:
            print(f"\n  ⚠ An unexpected error occurred: {str(e)}")
            input("\n  Press Enter to continue...")

if __name__ == "__main__":
    try:
        print_banner()
        print("  Initializing database...")
        initialize_database()
        print("  ✓ Database initialized successfully")
        print("  ✓ System ready")
        log_action("System", "Application started")
        input("\n  Press Enter to continue...")
        print()
        print()
        main_menu()
        
    except Exception as e:
        print(f"\n  ⚠ Fatal error during initialization: {str(e)}")
        print("  Application cannot start. Please contact support.\n")
        print_separator("=")
        sys.exit(1)
