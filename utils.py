import re
import datetime
# Define users with roles
USERS = {
    "Joe": {"password": "6v3Dsjx5wsLlCc", "role": "admin"},
    "Katy": {"password": "pass1", "role": "user"},
    "Annie": {"password": "pass1", "role": "user"},
    "Grace": {"password": "pass1", "role": "user"},
    "Will": {"password": "pass1", "role": "user"},
    "Laura": {"password": "pass1", "role": "user"},
    "Terry": {"password": "pass1", "role": "admin"}
}

def authenticate_user(username, password):
    user = USERS.get(username)
    return user if user and user['password'] == password else None

def calculate_log_summary():
    summary = {}
    log_pattern = re.compile(r"^(.*?) - (.*?) \(IP: (.*?)\): (.*?) \| Params: (.*)$")
    
    now = datetime.datetime.now()
    last_24_hours = now - datetime.timedelta(hours=24)
    last_30_days = now - datetime.timedelta(days=30)

    with open("user_activity.log", "r") as log_file:
        for line in log_file:
            match = log_pattern.match(line.strip())
            if match:
                timestamp_str, username, ip, action, _ = match.groups()
                summary[username] = summary.get(username, 0) + 1
    return summary

