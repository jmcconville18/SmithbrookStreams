from flask import Blueprint, jsonify
from tides import get_tide_data
from weather import get_weather_data
from pga import fetch_pga_data
from stocks import fetch_stock_data
from currentWeather import fetch_weather_data as fetch_current_weather
from forecast import fetch_forecast_data

data_bp = Blueprint('data', __name__)

@data_bp.route('/tides')
def tides():
    return jsonify(get_tide_data())

@data_bp.route('/weather')
def weather():
    return jsonify(get_weather_data())

@data_bp.route('/pga')
def pga():
    return jsonify(fetch_pga_data())

@data_bp.route('/stocks')
def stocks():
    return jsonify(fetch_stock_data())

@data_bp.route('/current-weather')
def current_weather():
    return jsonify(fetch_current_weather())

@data_bp.route('/forecast')
def forecast():
    return jsonify(fetch_forecast_data())

