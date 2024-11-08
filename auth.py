from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils import authenticate_user, USERS

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Make username case-insensitive
        entered_username = request.form['username'].strip().lower()
        password = request.form['password']
        
        # Authenticate user
        user = next((user for name, user in USERS.items() if name.lower() == entered_username), None)
        
        if user and user['password'] == password:
            # Set session variables
            session['username'] = entered_username
            session['role'] = user['role']
            
            # Debugging: Print confirmation that session variables are set
            print(f"Logged in as: {entered_username}, Role: {session['role']}")
            
            # Redirect to the home page (make sure the views Blueprint is correctly set up)
            return redirect(url_for('views.index'))
        else:
            flash('Invalid credentials')
    
    # Render the login page if not a POST request or if login fails
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    # Clear session and redirect to login page
    session.clear()
    return redirect(url_for('auth.login'))

