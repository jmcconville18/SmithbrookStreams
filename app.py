from flask import Flask
from auth import auth_bp
from admin import admin_bp
from data import data_bp
from metrics import metrics_bp
from views import views_bp  # Assuming you have a views Blueprint

app = Flask(__name__)
app.secret_key = '3XUpMyQSCo5nMzte'
app.config['SESSION_TYPE'] = 'filesystem'  # Ensure sessions are stored properly
app.config['SESSION_COOKIE_SECURE'] = True  # Ensure cookies work over HTTPS
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MediaRequests.db'

# Register Blueprints with appropriate URL prefixes
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(data_bp, url_prefix='/data')
app.register_blueprint(metrics_bp, url_prefix='/metrics')
app.register_blueprint(views_bp)  # No prefix for the main views

# print(app.url_map)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

