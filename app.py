from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import logging
from tides import get_tide_data
from weather import get_weather_data
from pga import fetch_pga_data
from stocks import fetch_stock_data
from currentWeather import fetch_weather_data
from forecast import fetch_forecast_data

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route('/tides', methods=['GET'])
def tides_endpoint():
    station_id = "8467150"  # Station ID for Bridgeport, CT
    tide_data = get_tide_data(station_id)
    return jsonify(tide_data)

@app.route('/weather', methods=['GET'])
def weather_endpoint():
    station_id = "8467150"  # Station ID for Bridgeport, CT
    weather_data = get_weather_data(station_id)
    return jsonify(weather_data)

@app.route('/pga', methods=['GET'])
def pga_scores_endpoint():
    pga_data = fetch_pga_data()
    return jsonify(pga_data)

@app.route('/stocks', methods=['GET'])
def stocks_endpoint():
    symbols = request.args.get('symbols', 'AAPL,MSFT,NVDA,CRM')
    stock_data = fetch_stock_data(symbols)
    return jsonify(stock_data)

@app.route('/current-weather', methods=['GET'])
def current_weather_endpoint():
    zip_code = request.args.get('zip_code', '06033')  # Default to 06033 if not provided
    weather_data = fetch_weather_data(zip_code)
    return jsonify(weather_data)

@app.route('/forecast', methods=['GET'])
def forecast_endpoint():
    zip_code = request.args.get('zip_code', '06033')  # Default to 06033 if not provided
    forecast_data = fetch_forecast_data(zip_code)
    return jsonify(forecast_data)

@app.route('/pga-scores', methods=['GET'])
def pga_scores_page():
    return render_template('pga.html')

@app.route('/stocks-page', methods=['GET'])
def stocks_page():
    return render_template('stocks.html')

@app.route('/weather-page', methods=['GET'])
def weather_page():
    return render_template('weather.html')

@app.route('/')
def index_page():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

