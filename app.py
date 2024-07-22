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
logging.basicConfig(filename='/home/joe/Documents/TickerWebsite/error.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route('/tides', methods=['GET'])
def tides_endpoint():
    try:
        station_id = "8467150"  # Station ID for Bridgeport, CT
        tide_data = get_tide_data(station_id)
        return jsonify(tide_data)
    except Exception as e:
        logging.exception("Error occurred in tides_endpoint")
        return jsonify({"error": str(e)}), 500

@app.route('/weather', methods=['GET'])
def weather_endpoint():
    try:
        station_id = "8467150"  # Station ID for Bridgeport, CT
        weather_data = get_weather_data(station_id)
        return jsonify(weather_data)
    except Exception as e:
        logging.exception("Error occurred in weather_endpoint")
        return jsonify({"error": str(e)}), 500

@app.route('/pga', methods=['GET'])
def pga_scores_endpoint():
    try:
        pga_data = fetch_pga_data()
        return jsonify(pga_data)
    except Exception as e:
        logging.exception("Error occurred in pga_scores_endpoint")
        return jsonify({"error": str(e)}), 500

@app.route('/stocks', methods=['GET'])
def stocks_endpoint():
    try:
        symbols = request.args.get('symbols', 'AAPL,MSFT,NVDA,CRM')
        stock_data = fetch_stock_data(symbols)
        return jsonify(stock_data)
    except Exception as e:
        logging.exception("Error occurred in stocks_endpoint")
        return jsonify({"error": str(e)}), 500

@app.route('/current-weather', methods=['GET'])
def current_weather_endpoint():
    try:
        zip_code = request.args.get('zip_code', '06033')  # Default to 06033 if not provided
        weather_data = fetch_weather_data(zip_code)
        return jsonify(weather_data)
    except Exception as e:
        logging.exception("Error occurred in current_weather_endpoint")
        return jsonify({"error": str(e)}), 500

@app.route('/forecast', methods=['GET'])
def forecast_endpoint():
    try:
        zip_code = request.args.get('zip_code', '06033')  # Default to 06033 if not provided
        forecast_data = fetch_forecast_data(zip_code)
        return jsonify(forecast_data)
    except Exception as e:
        logging.exception("Error occurred in forecast_endpoint")
        return jsonify({"error": str(e)}), 500

@app.route('/pga-scores', methods=['GET'])
def pga_scores_page():
    try:
        return render_template('pga.html')
    except Exception as e:
        logging.exception("Error occurred in pga_scores_page")
        return jsonify({"error": str(e)}), 500

@app.route('/stocks-page', methods=['GET'])
def stocks_page():
    try:
        return render_template('stocks.html')
    except Exception as e:
        logging.exception("Error occurred in stocks_page")
        return jsonify({"error": str(e)}), 500

@app.route('/weather-page', methods=['GET'])
def weather_page():
    try:
        return render_template('weather.html')
    except Exception as e:
        logging.exception("Error occurred in weather_page")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index_page():
    try:
        return render_template('index.html')
    except Exception as e:
        logging.exception("Error occurred in index_page")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

