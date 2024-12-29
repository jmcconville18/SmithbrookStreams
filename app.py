from flask import Flask #, Mail, Message
from flask_migrate import Migrate  # Import Flask-Migrate
from auth import auth_bp
from admin import admin_bp
from data import data_bp
from metrics import metrics_bp
from views import views_bp
from models import db  # Import the database instance
# from pushover import Client
import logging

# Configure logging to be less verbose
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = '3XUpMyQSCo5nMzte'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/joe/Documents/TickerWebsite/MediaRequests.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)  # Add this line

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(data_bp, url_prefix='/data')
app.register_blueprint(metrics_bp, url_prefix='/metrics')
app.register_blueprint(views_bp)

if __name__ == '__main__':
    app.run(debug=False)

