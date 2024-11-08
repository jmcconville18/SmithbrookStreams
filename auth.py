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
            session['username'] = entered_username
            session['role'] = user['role']
            return redirect(url_for('views.index'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

