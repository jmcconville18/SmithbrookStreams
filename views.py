from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, MediaRequest

views_bp = Blueprint('views', __name__)

# Home Page Route
@views_bp.route('/')
def index():
    # Check if the user is logged in
    if 'username' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('auth.login'))

    username = session.get('username')
    role = session.get('role')
    code = session.get('code')

    # Debugging
    print(f"Accessing index page - Username: {username}, Role: {role}, Code: {code}")
    return render_template('index.html', username=username, role=role, code=code)

# PGA Scores Page Route
@views_bp.route('/pga')
def pga():
    # Ensure user is logged in
    if 'username' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('auth.login'))

    username = session.get('username')
    role = session.get('role')

    # Debugging
    print(f"Accessing PGA page - Username: {username}, Role: {role}")
    return render_template('pga.html', username=username, role=role)# PGA Scores Page Route
    
@views_bp.route('/weather')
def weather():
    # Ensure user is logged in
    if 'username' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('auth.login'))

    username = session.get('username')
    role = session.get('role')

    # Debugging
    print(f"Accessing Weather page - Username: {username}, Role: {role}")
    return render_template('weather.html', username=username, role=role)
    
@views_bp.route('/stocks')
def stocks():
    # Ensure user is logged in
    if 'username' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('auth.login'))

    username = session.get('username')
    role = session.get('role')

    # Debugging
    print(f"Accessing Stocks page - Username: {username}, Role: {role}")
    return render_template('stocks.html', username=username, role=role)
    
# Media Requests Page
@views_bp.route('/media-requests', methods=['GET', 'POST'])
def media_requests():
    # Ensure user is logged in
    if 'username' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('auth.login'))

    # Debug session variables
    print(f"DEBUG: Logged in as: {session.get('username')}, Role: {session.get('role')}")

    if request.method == 'POST':
        # Handle new media request submission
        title = request.form.get('title')
        description = request.form.get('description')
        submitted_by = session.get('username')

        # Save to the database
        new_request = MediaRequest(
            title=title,
            description=description,
            submitted_by=submitted_by
        )
        db.session.add(new_request)
        db.session.commit()
        flash("Request submitted successfully!", "success")
        return redirect(url_for('views.media_requests'))

    # Fetch open and completed requests
    open_requests = MediaRequest.query.filter_by(status='Open').all()
    completed_requests = MediaRequest.query.filter_by(status='Completed').all()

    # Pass role and username explicitly to the template
    return render_template(
        'requests.html',
        open_requests=open_requests,
        completed_requests=completed_requests,
        role=session.get('role'),
        username=session.get('username')
    )

# Update Media Request (Admin Only)
@views_bp.route('/update-request/<int:id>', methods=['POST'])
def update_request(id):
    # Ensure user is logged in and is an admin
    if 'username' not in session or session.get('role') != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('views.media_requests'))

    request_to_update = MediaRequest.query.get_or_404(id)
    request_to_update.status = 'Completed'
    db.session.commit()
    flash("Request marked as completed.", "success")
    return redirect(url_for('views.media_requests'))

# Delete Media Request (Admin or Owner Only)
@views_bp.route('/delete-request/<int:id>', methods=['POST'])
def delete_request(id):
    # Ensure user is logged in
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('auth.login'))

    # Fetch the request to delete
    request_to_delete = MediaRequest.query.get_or_404(id)
    username = session.get('username')
    role = session.get('role')

    # Check if the user is authorized to delete the request
    if role != 'admin' and request_to_delete.submitted_by != username:
        flash("You are not authorized to delete this request.", "danger")
        return redirect(url_for('views.media_requests'))

    # Delete the request
    db.session.delete(request_to_delete)
    db.session.commit()
    flash("Request deleted successfully.", "success")
    return redirect(url_for('views.media_requests'))

