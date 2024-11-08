from flask import Blueprint, render_template, session, redirect, url_for, flash

admin_bp = Blueprint('admin', __name__)

# Ensure that the user has an admin role before accessing the admin routes
def admin_required():
    if session.get('role') != 'admin':
        flash('Access denied: Admins only.')
        return redirect(url_for('auth.login'))

@admin_bp.route('/view-logs')
def view_logs():
    # Check if the user is an admin
    if admin_required():
        return admin_required()
    # Your logic to display logs
    logs = []  # Replace with actual log fetching logic
    return render_template('view_logs.html', logs=logs)

@admin_bp.route('/system-monitor')
def system_monitor():
    # Check if the user is an admin
    if admin_required():
        return admin_required()
    # Your logic for system monitoring
    return render_template('system_monitor.html')

