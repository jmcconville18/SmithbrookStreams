from flask import Flask, jsonify, render_template, request, redirect, url_for, session, abort
from flask_cors import CORS
import logging
from tides import get_tide_data
from weather import get_weather_data
from pga import fetch_pga_data
from stocks import fetch_stock_data
from currentWeather import fetch_weather_data
from forecast import fetch_forecast_data
from functools import wraps
import datetime
import re
from collections import Counter
import datetime



def calculate_log_summary():
    summary = {}
    log_pattern = re.compile(r"^(.*?) - (.*?) \(IP: (.*?)\): (.*?) \| Params: (.*)$")
    
    now = datetime.datetime.now()
    last_24_hours = now - datetime.timedelta(hours=24)
    last_30_days = now - datetime.timedelta(days=30)

    with open("user_activity.log", "r") as log_file:
        for line in log_file:
            try:
                match = log_pattern.match(line.strip())
                if match:
                    timestamp_str, username, ip, action, _ = match.groups()
                    timestamp = datetime.datetime.strptime(timestamp_str.strip(), "%Y-%m-%d %I:%M:%S %p")
                    
                    if timestamp >= last_30_days:
                        # Initialize user's record if not present
                        if username not in summary:
                            summary[username] = {
                                "ip": ip,
                                "page_views_24h": 0,
                                "page_views_30d": 0,
                                "page_counts_30d": Counter()
                            }
                        
                        # Update 24-hour and 30-day page view counts
                        if timestamp >= last_24_hours:
                            summary[username]["page_views_24h"] += 1
                        summary[username]["page_views_30d"] += 1

                        # Exclude 'Home Page' and 'Logged In' from page counts
                        if action not in ['Home Page', 'Logged In']:
                            summary[username]["page_counts_30d"][action] += 1
            except Exception as e:
                logging.error(f"Error parsing log line: {line.strip()}. Error: {e}")
                continue

    # Calculate most visited page for each user
    for user_data in summary.values():
        # Exclude 'Home Page' and 'Logged In' from most visited page calculation
        if user_data["page_counts_30d"]:
            most_visited_page = user_data["page_counts_30d"].most_common(1)[0]
            user_data["most_visited_page_30d"] = f"{most_visited_page[0]} ({most_visited_page[1]})"
        else:
            user_data["most_visited_page_30d"] = "N/A"

    return summary

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = 'QeAT6vjSl3kNHv'  # Replace with a strong random key
CORS(app)  # Enable CORS

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

# Your secret code to be used in the session or as a query parameter
SECRET_CODE = "3XUpMyQSCo5nMzte"

# Function to log user activity with additional info (IP and params)
def log_activity(action):
    username = session.get("username", "Unknown")
    ip_address = request.remote_addr
    params = request.args.to_dict()
    params.pop('code', None)  # Remove 'code' if present

    with open("user_activity.log", "a") as log_file:
        log_file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')} - {username} (IP: {ip_address}): {action} | Params: {params}\n")

# Decorator to check if user has required role
def require_role(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            username = session.get("username")
            user = USERS.get(username)
            if user and user.get("role") == role:
                return func(*args, **kwargs)
            else:
                abort(403)  # Forbidden
        return wrapper
    return decorator

# Function decorator to check if the user has the secret code (either in session or URL)
def require_secret_code(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'code' in session and session['code'] == SECRET_CODE:
            return func(*args, **kwargs)
        elif request.args.get('code') == SECRET_CODE:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login', next=request.url))
    return decorated_function

# Login route to handle multiple users
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Make username case-insensitive by converting it to lowercase
        entered_username = request.form['username'].strip().lower()
        password = request.form['password']
        
        # Find the user in USERS dictionary using lowercase keys
        # You may normalize the dictionary once if modifying it is possible.
        user = next((user for name, user in USERS.items() if name.lower() == entered_username), None)
        
        # Check user credentials
        if user and user['password'] == password:
            # Set the secret code, username (case-insensitive), and role in the session upon successful login
            session['username'] = next(name for name in USERS if name.lower() == entered_username)
            session['role'] = user['role']
            session['code'] = SECRET_CODE
            log_activity("Logged In")
            next_page = request.args.get('next') or url_for('index_page')
            return redirect(next_page)
        else:
            error = "Invalid username or password. Please try again."
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/view-logs', methods=['GET'])
@require_secret_code
@require_role("admin")
def view_logs():
    logs = []
    log_summary = calculate_log_summary()  # Get the aggregated data
    
    log_pattern = re.compile(r"^(.*?) - (.*?) \(IP: (.*?)\): (.*?) \| Params: (.*)$")
    
    with open("user_activity.log", "r") as log_file:
        for line in log_file:
            try:
                match = log_pattern.match(line.strip())
                if match:
                    timestamp, username, ip_info, action, params = match.groups()
                    params = eval(params)  # Convert params string back to a dictionary
                    if "code" in params:
                        del params["code"]
                    logs.append({
                        "timestamp": timestamp.strip(),
                        "username": username.strip(),
                        "ip": ip_info.strip(),
                        "action": action.strip(),
                        "params": params
                    })
            except Exception as e:
                logging.error(f"Error parsing log line: {line.strip()}. Error: {e}")
                continue

    return render_template("view_logs.html", logs=logs, log_summary=log_summary)



# Routes that require the secret code (session or URL-based)
@app.route('/weather', methods=['GET'])
@require_secret_code
def weather_data_endpoint():
    log_activity("Weather Data")
    station_id = "8467150"
    weather_data = get_weather_data(station_id)
    return jsonify(weather_data)

@app.route('/tides', methods=['GET'])
@require_secret_code
def tides_data_endpoint():
    log_activity("Tides Data")
    station_id = "8467150"  # Station ID for Bridgeport, CT
    tide_data = get_tide_data(station_id)
    return jsonify(tide_data)

@app.route('/pga', methods=['GET'])
@require_secret_code
def pga_data_endpoint():
    log_activity("PGA Data")
    pga_data = fetch_pga_data()
    return jsonify(pga_data)

@app.route('/stocks', methods=['GET'])
@require_secret_code
def stocks_data_endpoint():
    log_activity("Stocks Data")
    symbols = request.args.get('symbols', 'AAPL,MSFT,NVDA,CRM')
    stock_data = fetch_stock_data(symbols)
    return jsonify(stock_data)

@app.route('/current-weather', methods=['GET'])
@require_secret_code
def current_weather_data_endpoint():
    log_activity("Current Weather Data")
    zip_code = request.args.get('zip_code', '06033')  # Default to 06033 if not provided
    weather_data = fetch_weather_data(zip_code)
    return jsonify(weather_data)

@app.route('/forecast', methods=['GET'])
@require_secret_code
def forecast_data_endpoint():
    log_activity("Forecast Data")
    zip_code = request.args.get('zip_code', '06033')  # Default to 06033 if not provided
    forecast_data = fetch_forecast_data(zip_code)
    return jsonify(forecast_data)

# HTML pages
@app.route('/pga-scores', methods=['GET'])
@require_secret_code
def pga_scores_page():
    log_activity("PGA Scores Page")
    return render_template('pga.html')

@app.route('/stocks-page', methods=['GET'])
@require_secret_code
def stocks_html_page():
    log_activity("Stocks Page")
    return render_template('stocks.html')

@app.route('/weather-page', methods=['GET'])
@require_secret_code
def weather_html_page():
    log_activity("Weather Page")
    return render_template('weather.html')

# Home page
@app.route('/')
@require_secret_code
def index_page():
    log_activity("Home Page")
    # Retrieve the role and username from the session
    role = session.get('role', 'guest')
    username = session.get('username', 'Guest')
    return render_template('index.html', role=role, username=username)

@app.route('/logout')
def logout():
    log_activity("Logged Out")
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

