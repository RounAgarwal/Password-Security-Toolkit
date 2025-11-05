import datetime
import pandas as pd
import numpy as np
from pathlib import Path

LOG_FILE = "activity.log"

def log_action(username, action):
    with open(LOG_FILE, "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {username}: {action}\n")

def view_logs():
    try:
        with open(LOG_FILE, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "No logs available."

def get_logs_dataframe():
    try:
        if not Path(LOG_FILE).exists():
            return pd.DataFrame(columns=['Timestamp', 'Username', 'Action'])
        
        logs = []
        with open(LOG_FILE, "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split("] ", 1)
                    if len(parts) == 2:
                        timestamp = parts[0].replace("[", "")
                        rest = parts[1].split(": ", 1)
                        if len(rest) == 2:
                            username, action = rest
                            logs.append({
                                'Timestamp': timestamp,
                                'Username': username,
                                'Action': action
                            })
        
        return pd.DataFrame(logs)
    except Exception as e:
        return pd.DataFrame(columns=['Timestamp', 'Username', 'Action'])

def get_user_activity_summary(username):
    df = get_logs_dataframe()
    if df.empty:
        return None
    
    user_logs = df[df['Username'] == username]
    if user_logs.empty:
        return None
    
    summary = {
        'total_actions': len(user_logs),
        'login_count': len(user_logs[user_logs['Action'].str.contains('Logged in', case=False, na=False)]),
        'last_action': user_logs.iloc[-1]['Action'] if not user_logs.empty else 'N/A',
        'last_seen': user_logs.iloc[-1]['Timestamp'] if not user_logs.empty else 'N/A',
        'actions_breakdown': user_logs['Action'].value_counts().to_dict()
    }
    
    return summary

def get_activity_statistics():
    df = get_logs_dataframe()
    if df.empty:
        return None
    
    stats = {
        'total_logs': len(df),
        'unique_users': df['Username'].nunique(),
        'most_active_user': df['Username'].mode()[0] if not df.empty else 'N/A',
        'actions_per_user': df.groupby('Username').size().to_dict(),
        'recent_activity': df.tail(10).to_dict('records')
    }
    
    return stats

def display_logs_table(limit=None):
    df = get_logs_dataframe()
    if df.empty:
        return "No logs available."
    
    if limit:
        df = df.tail(limit)
    
    output = "\n"
    output += "=" * 100 + "\n"
    output += f"{'TIMESTAMP':<20} {'USERNAME':<20} {'ACTION':<60}\n"
    output += "=" * 100 + "\n"
    
    for _, row in df.iterrows():
        output += f"{row['Timestamp']:<20} {row['Username']:<20} {row['Action']:<60}\n"
    
    output += "=" * 100 + "\n"
    
    return output
