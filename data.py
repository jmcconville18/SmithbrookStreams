from flask import Blueprint, jsonify, request
from tides import get_tide_data
from weather import get_weather_data
from pga import fetch_pga_data
from stocks import fetch_stock_data
from currentWeather import fetch_weather_data as fetch_current_weather
from forecast import fetch_forecast_data

data_bp = Blueprint('data', __name__)

DEFAULT_STATION_ID = "8467150"  # Station ID for Bridgeport, CT

def validate_code():
    """Validate the code from the query string."""
    code = request.args.get('code')
    return code == '3XUpMyQSCo5nMzte'

# Route for tides data
@data_bp.route('/tides')
def tides():
    if not validate_code():
        return jsonify({"error": "Invalid code"}), 403

    # Get station_id from query parameters, or use default if not provided
    station_id = request.args.get('station_id', DEFAULT_STATION_ID)
    return jsonify(get_tide_data(station_id))

# Route for weather data
@data_bp.route('/weather')
def weather():
    if not validate_code():
        return jsonify({"error": "Invalid code"}), 403

    # Get station_id from query parameters, or use default if not provided
    station_id = request.args.get('station_id', DEFAULT_STATION_ID)
    return jsonify(get_weather_data(station_id))

# Route for PGA data
@data_bp.route('/pga')
def pga():
    if not validate_code():
        return jsonify({"error": "Invalid code"}), 403
    return jsonify(fetch_pga_data())

# Route for stocks data
@data_bp.route('/stocks')
def stocks():
    if not validate_code():
        return jsonify({"error": "Invalid code"}), 403
    symbols = request.args.get('symbols', '')
    return jsonify(fetch_stock_data(symbols))

# Route for current weather data
@data_bp.route('/current-weather')
def current_weather():
    if not validate_code():
        return jsonify({"error": "Invalid code"}), 403
    return jsonify(fetch_current_weather())

# Route for forecast data
@data_bp.route('/forecast')
def forecast():
    if not validate_code():
        return jsonify({"error": "Invalid code"}), 403
    return jsonify(fetch_forecast_data())

