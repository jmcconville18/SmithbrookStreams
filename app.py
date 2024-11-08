from flask import Flask
from auth import auth_bp
from admin import admin_bp
from data import data_bp
from metrics import metrics_bp

app = Flask(__name__)
app.secret_key = '3XUpMyQSCo5nMzte'

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(data_bp)
app.register_blueprint(metrics_bp)

if __name__ == '__main__':
    app.run(debug=True)

