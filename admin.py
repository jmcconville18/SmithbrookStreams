from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/system-monitor')
@admin_required
def system_monitor():
    return render_template('system_monitor.html')

