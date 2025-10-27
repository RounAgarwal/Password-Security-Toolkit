# Password & Security Toolkit

The **Password & Security Toolkit** is a secure, menu-driven application built in Python for managing user credentials and enforcing security best practices. It includes role-based access for Admins and Users, full database integration, and strong encryption for stored passwords.

## Key Features

### User Functions
- Register and await admin approval.
- Secure login using hashed credentials.
- Generate strong, random passwords.
- Save, view, update, and delete stored passwords.
- Passwords stored with AES encryption for maximum security.
- Password strength checker for improved safety.

### Admin Functions
- Dedicated admin login panel.
- Approve or reject user registrations.
- Suspend or unsuspend user accounts.
- View activity logs and user database statistics.
- Perform database maintenance.

### Security
- Passwords hashed using SHA-256 before storage.
- Data encryption handled via the `cryptography` (Fernet) module.
- User passwords and operations securely logged.
- Automatic database and key initialization on first run.

## Requirements

Install dependencies before running the toolkit:

```bash
pip install -r requirements.txt
```

## How to Run

```bash
python main.py
```

## Admin Login Credentials

```bash
User: admin
Passowrd: admin123
```

The application automatically initializes the database (`toolkit.db`), encryption key (`secret.key`), and activity log on first execution.

## Project Files

| File / Folder | Description |
|----------------|-------------|
| `main.py` | Entry point, handles main menu logic. |
| `modules/` | Contains all Python modules (admin, user, security, DB, logging). |
| `requirements.txt` | Python dependencies for quick setup. |
| `toolkit.db` | SQLite database (auto-generated). |
| `secret.key` | Encryption key (auto-generated). |
| `activity.log` | Logs user and admin activities. |

## License

Licensed under the **MIT License** — you are free to use and modify the project with attribution.

---
**Author:** Rounak Agarwal  
**Version:** 1.0  
**Language:** Python 3.x
