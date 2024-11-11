from flask import Blueprint, render_template, jsonify
import datetime
import re
import psutil
from collections import defaultdict

admin_bp = Blueprint('admin', __name__)

# Existing functions for log management
def get_logs():
    """
    Function to read and return all logs from 'user_activity.log'.
    """
    logs = []
    log_pattern = re.compile(r"^(.*?) - (.*?) \(IP: (.*?)\): (.*?) \| Params: (.*)$")

    with open("user_activity.log", "r") as log_file:
        for line in log_file:
            match = log_pattern.match(line.strip())
            if match:
                timestamp_str, username, ip, action, params = match.groups()
                logs.append({
                    'timestamp': timestamp_str,
                    'username': username,
                    'ip': ip,
                    'action': action,
                    'params': params
                })
    return logs

def calculate_log_summary():
    """
    Function to generate a summary of user activity logs.
    """
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
                
                # Updated timestamp parsing with AM/PM support
                timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %I:%M:%S %p")
                
                # Initialize the user's IP if not set
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


@admin_bp.route('/view_logs')
def view_logs():
    """
    Route to display user activity logs and summary.
    """
    try:
        logs = get_logs()
        log_summary = calculate_log_summary()
        return render_template('view_logs.html', logs=logs, log_summary=log_summary)
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return render_template('error.html', error_message=str(e))

@admin_bp.route('/system_monitor')
def system_monitor():
    """
    Route to display system monitoring information.
    """
    try:
        return render_template('system_monitor.html')
    except Exception as e:
        print(f"Error in system monitor: {e}")
        return render_template('error.html', error_message=str(e))

# New API endpoint for real-time server stats
@admin_bp.route('/admin/api/server-stats')
def server_stats():
    """
    API endpoint to return server resource usage as JSON.
    """
    try:
        data = {
            'cpu': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent,
            'joedrive': psutil.disk_usage('/mnt/JoeDrive').percent
        }
        return jsonify(data)
    except Exception as e:
        print(f"Error fetching server stats: {e}")
        return jsonify({'error': str(e)}), 500

