from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils import USERS  # Assuming USERS is defined in utils.py

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Initialize error message
    if request.method == 'POST':
        entered_username = request.form['username'].strip().lower()
        password = request.form['password']

        print(f"Attempting login for user: {entered_username}")

        # Authenticate user
        user = next((user for name, user in USERS.items() if name.lower() == entered_username), None)

        # Check if user exists
        if not user:
            error = "Username not found."
            print("Error: Username not found.")
        elif user['password'] != password:
            error = "Incorrect password."
            print("Error: Incorrect password.")
        else:
            # Set session variables on successful login
            session['username'] = entered_username
            session['role'] = user['role']
            session['code'] = '3XUpMyQSCo5nMzte'
            
            # Debugging prints
            print(f"Session Username: {session.get('username')}")
            print(f"Session Role: {session.get('role')}")
            print(f"Session Code: {session.get('code')}")

            return redirect(url_for('views.index'))

    # Always render the login page if it's a GET request or if there was an error
    return render_template('login.html', error=error)

@auth_bp.route('/logout')
def logout():
    # Clear the session to log out the user
    session.clear()
    print("User logged out")
    return redirect(url_for('auth.login'))

