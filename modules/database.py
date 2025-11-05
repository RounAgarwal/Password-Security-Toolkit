import sqlite3
import pandas as pd
import numpy as np
from modules.security_utils import hash_password, encrypt_password, decrypt_password

DB_NAME = "toolkit.db"

def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    status TEXT DEFAULT 'Pending')''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    purpose TEXT,
                    organization TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    label TEXT,
                    password TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    feedback TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'Pending',
                    FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS account_locks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    reason TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'Locked',
                    FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS audit_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'Pending',
                    FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    conn.commit()
    conn.close()

def add_user(username, password, name=None, email=None, purpose=None, organization=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                  (username, hash_password(password)))
        user_id = c.lastrowid
        
        c.execute("INSERT INTO user_profiles (user_id, name, email, purpose, organization) VALUES (?, ?, ?, ?, ?)",
                  (user_id, name, email, purpose, organization))
        
        conn.commit()
        result = True
    except:
        result = False
    conn.close()
    return result

def get_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", 
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_name(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_audit_requests(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, timestamp, status FROM audit_requests WHERE user_id=? ORDER BY timestamp DESC", (user_id,))
    audits = c.fetchall()
    conn.close()
    return audits

def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""SELECT u.id, u.username, u.status, p.name, p.email 
                 FROM users u 
                 LEFT JOIN user_profiles p ON u.id = p.user_id""")
    users = c.fetchall()
    conn.close()
    return users

def get_user_profile(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name, email, purpose, organization FROM user_profiles WHERE user_id=?", (user_id,))
    profile = c.fetchone()
    conn.close()
    return profile

def update_user_status(user_id, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET status=? WHERE id=?", (status, user_id))
    conn.commit()
    conn.close()

def add_password(user_id, label, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO passwords (user_id, label, password) VALUES (?, ?, ?)", 
              (user_id, label, encrypt_password(password)))
    conn.commit()
    conn.close()

def get_passwords(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, label, password FROM passwords WHERE user_id=?", (user_id,))
    records = c.fetchall()
    conn.close()
    return [(r[0], r[1], decrypt_password(r[2])) for r in records]

def get_passwords_dataframe(user_id):
    records = get_passwords(user_id)
    if not records:
        return pd.DataFrame(columns=['ID', 'Label', 'Password'])
    
    df = pd.DataFrame(records, columns=['ID', 'Label', 'Password'])
    return df

def update_password(record_id, new_password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE passwords SET password=? WHERE id=?", 
              (encrypt_password(new_password), record_id))
    conn.commit()
    conn.close()

def delete_password(record_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM passwords WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

def add_feedback(user_id, username, feedback):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO feedback (user_id, username, feedback) VALUES (?, ?, ?)",
              (user_id, username, feedback))
    conn.commit()
    conn.close()

def get_all_feedback():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username, feedback, timestamp, status FROM feedback ORDER BY timestamp DESC")
    feedback = c.fetchall()
    conn.close()
    return feedback

def mark_feedback_resolved(feedback_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE feedback SET status='Resolved' WHERE id=?", (feedback_id,))
    conn.commit()
    conn.close()

def lock_user_account(user_id, username, reason):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET status='Locked' WHERE id=?", (user_id,))
    c.execute("INSERT INTO account_locks (user_id, username, reason) VALUES (?, ?, ?)",
              (user_id, username, reason))
    conn.commit()
    conn.close()

def request_account_unlock(user_id, username, reason):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE account_locks SET reason=?, status='Unlock Requested' WHERE user_id=? AND status='Locked'",
              (reason, user_id))
    if c.rowcount == 0:
        c.execute("INSERT INTO account_locks (user_id, username, reason, status) VALUES (?, ?, ?, 'Unlock Requested')",
                  (user_id, username, reason))
    conn.commit()
    conn.close()

def get_account_lock_requests():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username, reason, timestamp FROM account_locks WHERE status='Unlock Requested' ORDER BY timestamp DESC")
    requests = c.fetchall()
    conn.close()
    return requests

def unlock_user_account(request_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM account_locks WHERE id=?", (request_id,))
    result = c.fetchone()
    if result:
        user_id = result[0]
        c.execute("UPDATE users SET status='Approved' WHERE id=?", (user_id,))
        c.execute("UPDATE account_locks SET status='Unlocked' WHERE id=?", (request_id,))
        conn.commit()
    conn.close()

def add_audit_request(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO audit_requests (user_id, username) VALUES (?, ?)",
              (user_id, username))
    conn.commit()
    conn.close()

def get_audit_requests():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username, timestamp, status FROM audit_requests WHERE status='Pending' ORDER BY timestamp DESC")
    requests = c.fetchall()
    conn.close()
    return requests

def mark_audit_completed(audit_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE audit_requests SET status='Completed' WHERE id=?", (audit_id,))
    conn.commit()
    conn.close()

def get_user_statistics():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    c.execute("SELECT status, COUNT(*) FROM users GROUP BY status")
    status_counts = dict(c.fetchall())
    
    c.execute("SELECT COUNT(*) FROM passwords")
    total_passwords = c.fetchone()[0]
    
    conn.close()
    
    return {
        'total_users': total_users,
        'status_breakdown': status_counts,
        'total_passwords': total_passwords
    }

def get_user_completed_audits(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username, timestamp, status FROM audit_requests WHERE user_id=? AND status='Completed' ORDER BY timestamp DESC", (user_id,))
    audits = c.fetchall()
    conn.close()
    return audits

