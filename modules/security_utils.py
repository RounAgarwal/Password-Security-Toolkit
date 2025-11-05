import hashlib
import secrets
import string
from cryptography.fernet import Fernet
import os
import numpy as np

KEY_FILE = "secret.key"

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    with open(KEY_FILE, "rb") as f:
        return f.read()

key = load_key()
fernet = Fernet(key)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def encrypt_password(password):
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted):
    return fernet.decrypt(encrypted.encode()).decode()

def generate_password(length=12, use_special=True, use_numbers=True, use_uppercase=True, use_lowercase=True):
    chars = ""
    if use_lowercase:
        chars += string.ascii_lowercase
    if use_uppercase:
        chars += string.ascii_uppercase
    if use_numbers:
        chars += string.digits
    if use_special:
        chars += string.punctuation
    
    if not chars:
        chars = string.ascii_letters + string.digits
    
    return ''.join(secrets.choice(chars) for _ in range(length))

def check_strength(password):
    score = 0
    feedback = []
    
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Add lowercase letters")
    
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Add uppercase letters")
    
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Add numbers")
    
    if any(c in string.punctuation for c in password):
        score += 1
    else:
        feedback.append("Add special characters")
    
    if len(password) >= 12:
        score += 1
    else:
        feedback.append(f"Increase length (current: {len(password)}, recommended: 12+)")
    
    if score <= 2:
        strength = "Weak"
        color = "🔴"
    elif score == 3:
        strength = "Moderate"
        color = "🟡"
    elif score == 4:
        strength = "Strong"
        color = "🟢"
    else:
        strength = "Very Strong"
        color = "🟢"
    
    return {
        'strength': strength,
        'score': score,
        'max_score': 5,
        'percentage': (score / 5) * 100,
        'feedback': feedback,
        'color': color
    }

def analyze_password_entropy(password):
    if not password:
        return 0
    
    char_set_size = 0
    if any(c.islower() for c in password):
        char_set_size += 26
    if any(c.isupper() for c in password):
        char_set_size += 26
    if any(c.isdigit() for c in password):
        char_set_size += 10
    if any(c in string.punctuation for c in password):
        char_set_size += len(string.punctuation)
    
    entropy = len(password) * np.log2(char_set_size) if char_set_size > 0 else 0
    return round(entropy, 2)

def compare_passwords(password1, password2):
    strength1 = check_strength(password1)
    strength2 = check_strength(password2)
    entropy1 = analyze_password_entropy(password1)
    entropy2 = analyze_password_entropy(password2)
    
    return {
        'password1': {
            'strength': strength1['strength'],
            'score': strength1['score'],
            'entropy': entropy1
        },
        'password2': {
            'strength': strength2['strength'],
            'score': strength2['score'],
            'entropy': entropy2
        },
        'recommendation': 'Password 1' if strength1['score'] >= strength2['score'] else 'Password 2'
    }

def generate_multiple_passwords(count=5, length=12):
    passwords = []
    for _ in range(count):
        pwd = generate_password(length)
        strength = check_strength(pwd)
        entropy = analyze_password_entropy(pwd)
        passwords.append({
            'password': pwd,
            'strength': strength['strength'],
            'entropy': entropy
        })
    return passwords

def validate_password_requirements(password, min_length=8, require_upper=True, require_lower=True, require_digit=True, require_special=True):
    errors = []
    
    if len(password) < min_length:
        errors.append(f"Password must be at least {min_length} characters")
    
    if require_upper and not any(c.isupper() for c in password):
        errors.append("Password must contain uppercase letters")
    
    if require_lower and not any(c.islower() for c in password):
        errors.append("Password must contain lowercase letters")
    
    if require_digit and not any(c.isdigit() for c in password):
        errors.append("Password must contain digits")
    
    if require_special and not any(c in string.punctuation for c in password):
        errors.append("Password must contain special characters")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }
