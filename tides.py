import requests
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def get_tide_data(station_id):
    try:
        url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

        # Calculate the dates
        today = datetime.now()
        prev_day = (today - timedelta(days=1)).strftime('%Y%m%d')
        next_day = (today + timedelta(days=1)).strftime('%Y%m%d')

        # Fetch data for the previous day, current day, and next day
        params = {
            "begin_date": prev_day,
            "end_date": next_day,
            "station": station_id,
            "product": "predictions",
            "datum": "MLLW",
            "units": "english",
            "time_zone": "lst_ldt",
            "application": "NOS.COOPS.TAC.WL",
            "format": "json"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        tide_data = response.json()

        predictions = tide_data['predictions']

        # Find current tide, next high tide, and next low tide
        next_high_tide = None
        next_low_tide = None
        current_tide = None
        now = datetime.now()

        for i in range(1, len(predictions) - 1):
            current_prediction = predictions[i]
            prev_prediction = predictions[i - 1]
            next_prediction = predictions[i + 1]

            current_time = datetime.strptime(current_prediction['t'], "%Y-%m-%d %H:%M")
            prev_time = datetime.strptime(prev_prediction['t'], "%Y-%m-%d %H:%M")
            next_time = datetime.strptime(next_prediction['t'], "%Y-%m-%d %H:%M")

            if prev_time <= now <= next_time:
                current_tide = {'time': now, 'value': current_prediction['v']}

            if float(prev_prediction['v']) <= float(current_prediction['v']) >= float(next_prediction['v']):
                if current_time > now and (next_high_tide is None or current_time < next_high_tide['time']):
                    next_high_tide = {'time': current_time, 'value': current_prediction['v']}

            if float(prev_prediction['v']) >= float(current_prediction['v']) <= float(next_prediction['v']):
                if current_time > now and (next_low_tide is None or current_time < next_low_tide['time']):
                    next_low_tide = {'time': current_time, 'value': current_prediction['v']}

        return {
            'current_tide': {
                'time': current_tide['time'].strftime('%Y-%m-%d %H:%M:%S'),
                'value': current_tide['value']
            },
            'next_high_tide': {
                'time': next_high_tide['time'].strftime('%Y-%m-%d %H:%M:%S'),
                'value': next_high_tide['value']
            },
            'next_low_tide': {
                'time': next_low_tide['time'].strftime('%Y-%m-%d %H:%M:%S'),
                'value': next_low_tide['value']
            }
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return {"error": "Failed to fetch tide data"}
    except Exception as e:
        logging.error(f"Error processing tide data: {e}")
        return {"error": "Internal server error"}

