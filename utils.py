import re
import datetime
from collections import defaultdict
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
    summary = defaultdict(lambda: {
        'ip': None,
        'page_views_24h': 0,
        'page_views_30d': 0,
        'most_visited_page_30d': {}
    })
    
    log_pattern = re.compile(r"^(.*?) - (.*?) \(IP: (.*?)\): (.*?) \| Params: (.*)$")
    
    now = datetime.datetime.now()
    last_24_hours = now - datetime.timedelta(hours=24)
    last_30_days = now - datetime.timedelta(days=30)
    
    with open("user_activity.log", "r") as log_file:
        for line in log_file:
            match = log_pattern.match(line.strip())
            if match:
                timestamp_str, username, ip, action, params = match.groups()
                timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                
                # Initialize the user's data if not already present
                if not summary[username]['ip']:
                    summary[username]['ip'] = ip
                
                # Count page views in the last 24 hours and 30 days
                if timestamp >= last_24_hours:
                    summary[username]['page_views_24h'] += 1
                if timestamp >= last_30_days:
                    summary[username]['page_views_30d'] += 1
                
                # Track the most visited page
                page = params.split('=')[1] if '=' in params else params
                if page:
                    summary[username]['most_visited_page_30d'][page] = summary[username]['most_visited_page_30d'].get(page, 0) + 1
    
    # Determine the most visited page for each user
    for username, data in summary.items():
        if data['most_visited_page_30d']:
            data['most_visited_page_30d'] = max(data['most_visited_page_30d'], key=data['most_visited_page_30d'].get)
        else:
            data['most_visited_page_30d'] = "None"
    
    return summary
