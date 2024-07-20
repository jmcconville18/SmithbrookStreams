import requests
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

STOCK_API_KEY = 'f972882b314a45ec94268d736a4111a8'
STOCK_API_URL = 'https://api.twelvedata.com/time_series'

def fetch_stock_data(symbols):
    try:
        params = {
            'symbol': symbols,
            'interval': '1day',
            'apikey': STOCK_API_KEY
        }

        logging.debug(f"Fetching stock data for symbols: {symbols}")
        response = requests.get(STOCK_API_URL, params=params)
        
        # Log the response text for debugging
        logging.debug(f"API Response: {response.text}")
        
        response.raise_for_status()
        stock_data = response.json()

        stock_data_list = []
        for symbol, data in stock_data.items():
            if 'values' not in data:
                continue

            values = data['values']
            latest = values[0]
            previous = values[1]

            close = float(latest['close'])
            prev_close = float(previous['close'])
            change = close - prev_close
            percent_change = (change / prev_close) * 100

            week_ma = calculate_moving_average(values, 7)
            week_change = close - week_ma
            week_percent_change = (week_change / week_ma) * 100

            month_ma = calculate_moving_average(values, 30)
            month_change = close - month_ma
            month_percent_change = (month_change / month_ma) * 100

            stock_data_list.append({
                "symbol": symbol,
                "date": latest['datetime'],
                "open": float(latest['open']),
                "high": float(latest['high']),
                "low": float(latest['low']),
                "close": close,
                "volume": latest['volume'],
                "change": change,
                "percent_change": percent_change,
                "7_day_ma": week_ma,
                "7_day_change": week_change,
                "7_day_percent_change": week_percent_change,
                "30_day_ma": month_ma,
                "30_day_change": month_change,
                "30_day_percent_change": month_percent_change
            })

        return stock_data_list

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return {"error": "Failed to fetch stock data"}
    except Exception as e:
        logging.error(f"Error fetching stock data: {e}")
        return {"error": "Failed to fetch stock data"}

def calculate_moving_average(values, days):
    relevant_values = values[:days]
    total = sum(float(value['close']) for value in relevant_values)
    return total / len(relevant_values)

