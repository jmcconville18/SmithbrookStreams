from flask import Flask
from auth import auth_bp
from admin import admin_bp
from data import data_bp
from metrics import metrics_bp
from views import views_bp  # Import the new Blueprint

app = Flask(__name__)
app.secret_key = '3XUpMyQSCo5nMzte'

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(data_bp)
app.register_blueprint(metrics_bp)
app.register_blueprint(views_bp)  # Register the new Blueprint

if __name__ == '__main__':
    app.run(debug=True)

