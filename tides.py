import requests
import datetime
import pytz
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

TIDES_API_URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
STATION_ID = "8467150"  # Bridgeport, CT
EST = pytz.timezone('US/Eastern')

def get_tide_data(station_id):
    try:
        # Calculate dynamic dates
        today = datetime.datetime.now(EST)
        tomorrow = today + datetime.timedelta(days=1)
        begin_date = today.strftime('%Y%m%d')
        end_date = tomorrow.strftime('%Y%m%d')

        # Fetch predictions for high and low tides
        params = {
            'product': 'predictions',
            'application': 'NOS.COOPS.TAC.WL',
            'begin_date': begin_date,
            'end_date': end_date,
            'datum': 'MLLW',
            'station': station_id,
            'time_zone': 'lst_ldt',
            'units': 'english',
            'interval': 'hilo',
            'format': 'json'
        }
        response = requests.get(TIDES_API_URL, params=params)
        response.raise_for_status()
        predictions_data = response.json()

        predictions = predictions_data.get('predictions', [])
        current_time = datetime.datetime.now(EST)

        logging.debug(f"Current time: {current_time}")

        # Initialize variables
        next_high_tide = None
        next_low_tide = None
        current_tide = {'time': current_time.strftime('%Y-%m-%d %H:%M:%S %Z'), 'value': None}

        # Iterate through predictions to identify the next high and low tides
        for prediction in predictions:
            tide_time = datetime.datetime.strptime(prediction['t'], '%Y-%m-%d %H:%M')
            tide_time = EST.localize(tide_time)  # Assume the API returns times in EST
            tide_value = float(prediction['v'])
            tide_type = prediction['type']

            if tide_time > current_time:
                logging.debug(f"Checking tide at {tide_time} with value {tide_value} and type {tide_type}")

                if tide_type == 'H' and (next_high_tide is None or tide_time < next_high_tide['time']):
                    next_high_tide = {'time': tide_time, 'value': tide_value}
                    logging.debug(f"New next high tide found: {next_high_tide}")

                if tide_type == 'L' and (next_low_tide is None or tide_time < next_low_tide['time']):
                    next_low_tide = {'time': tide_time, 'value': tide_value}
                    logging.debug(f"New next low tide found: {next_low_tide}")

        # Fetch current water level
        water_level_params = {
            'product': 'water_level',
            'application': 'NOS.COOPS.TAC.WL',
            'station': station_id,
            'datum': 'MLLW',
            'time_zone': 'lst_ldt',
            'units': 'english',
            'format': 'json',
            'begin_date': today.strftime('%Y%m%d'),
            'end_date': tomorrow.strftime('%Y%m%d')
        }
        water_level_response = requests.get(TIDES_API_URL, params=water_level_params)
        water_level_response.raise_for_status()
        water_level_data = water_level_response.json()
        water_level_predictions = water_level_data.get('data', [])

        # Find the closest tide entry to the current time
        closest_tide = None
        min_time_diff = float('inf')

        for prediction in water_level_predictions:
            tide_time = datetime.datetime.strptime(prediction['t'], '%Y-%m-%d %H:%M')
            tide_time = EST.localize(tide_time)
            time_diff = abs((tide_time - current_time).total_seconds())

            if time_diff < min_time_diff:
                closest_tide = prediction
                min_time_diff = time_diff

        if closest_tide:
            current_tide['value'] = closest_tide['v']

        # Calculate metrics
        metrics = {}
        if next_high_tide and next_low_tide:
            next_tide_time = min(next_high_tide['time'], next_low_tide['time'])
            next_tide = next_high_tide if next_high_tide['time'] == next_tide_time else next_low_tide
            following_tide = next_high_tide if next_high_tide['time'] != next_tide_time else next_low_tide

            minutes_between_tides = (following_tide['time'] - next_tide['time']).total_seconds() / 60
            minutes_until_next_tide = (next_tide['time'] - current_time).total_seconds() / 60
            percent_to_next_tide = minutes_until_next_tide / minutes_between_tides if minutes_between_tides != 0 else 0

            metrics = {
                'minutes_between_tides': round(minutes_between_tides, 2),
                'minutes_until_next_tide': round(minutes_until_next_tide, 2),
                'percent_to_next_tide': round(percent_to_next_tide, 2)
            }

        # Format times for JSON response
        if next_high_tide:
            next_high_tide['time'] = next_high_tide['time'].strftime('%Y-%m-%d %H:%M:%S %Z')
        if next_low_tide:
            next_low_tide['time'] = next_low_tide['time'].strftime('%Y-%m-%d %H:%M:%S %Z')

        api_url = {
            'predictions_url': response.url,
            'water_level_url': water_level_response.url
        }

        return {
            'current_tide': current_tide,
            'next_high_tide': next_high_tide,
            'next_low_tide': next_low_tide,
            'metrics': metrics,
            'api_url': api_url
        }

    except requests.RequestException as e:
        logging.error(f"Error fetching tide data: {e}")
        return {'error': 'Failed to fetch tide data', 'api_url': {'predictions_url': response.url if response else TIDES_API_URL, 'water_level_url': water_level_response.url if water_level_response else TIDES_API_URL}}

# Example usage
if __name__ == '__main__':
    tide_data = get_tide_data(STATION_ID)
    print(tide_data)

