from flask import Blueprint, render_template, session, redirect, url_for, flash
from pga import fetch_pga_data  # Import the function that fetches PGA data
from stocks import fetch_stock_data  # Import the function for fetching stock data
from weather import get_weather_data  # Import the function for fetching weather data
from models import db, MediaRequest
from flask_login import current_user, login_required

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    # Check if the user is logged in
    if 'username' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('auth.login'))

    # Retrieve session variables
    username = session.get('username')
    role = session.get('role')
    code = session.get('code')

    print(f"Accessing index page - Username: {username}, Role: {role}, Code: {code}")

    # Pass the session variables to the template
    return render_template('index.html', username=username, role=role, code=code)


@app.route('/media-requests', methods=['GET', 'POST'])
@login_required
def media_requests():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        submitted_by = current_user.username if current_user.is_authenticated else 'Anonymous'
        
        new_request = MediaRequest(
            title=title,
            description=description,
            submitted_by=submitted_by
        )
        db.session.add(new_request)
        db.session.commit()
        flash("Request submitted successfully!", "success")
        return redirect(url_for('media_requests'))

    open_requests = MediaRequest.query.filter_by(status='Open').all()
    completed_requests = MediaRequest.query.filter_by(status='Completed').all()
    return render_template('requests.html', open_requests=open_requests, completed_requests=completed_requests)

@app.route('/update-request/<int:id>', methods=['POST'])
@login_required
def update_request(id):
    if current_user.role != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('media_requests'))

    request_to_update = MediaRequest.query.get_or_404(id)
    request_to_update.status = 'Completed'
    db.session.commit()
    flash("Request marked as completed.", "success")
    return redirect(url_for('media_requests'))
    
@views_bp.route('/pga-scores')
def pga_scores():
    # Check if the user is logged in
    if 'username' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('auth.login'))

    code = session.get('code')
    scores = fetch_pga_data()
    return render_template('pga.html', scores=scores, code=code)


@views_bp.route('/stocks-page')
def stocks_page():
    # Check if the user is logged in or has the correct code
    if 'username' not in session or session.get('code') != '3XUpMyQSCo5nMzte':
        flash('Please log in to access this page.')
        return redirect(url_for('auth.login'))

    code = session.get('code')
    symbols = 'AAPL,MSFT,NVDA,CRM'
    stock_data = fetch_stock_data(symbols)
    return render_template('stocks.html', stock_data=stock_data, code=code)


@views_bp.route('/weather-page')
def weather_page():
    # Check if the user is logged in or has the correct code
    if 'username' not in session or session.get('code') != '3XUpMyQSCo5nMzte':
        flash('Please log in to access this page.')
        return redirect(url_for('auth.login'))

    code = session.get('code')
    station_id = "8467150"  # Default station ID for Bridgeport, CT
    weather_data = get_weather_data(station_id)
    return render_template('weather.html', weather_data=weather_data, code=code)

