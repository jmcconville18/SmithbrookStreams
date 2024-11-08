from flask import Blueprint, render_template, session, redirect, url_for, flash

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

    # Debugging prints
    print(f"Accessing index page - Username: {username}, Role: {role}, Code: {code}")

    # Pass the session variables to the template
    return render_template('index.html', username=username, role=role, code=code)

