import requests
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def fetch_product(station_id, product):
    url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "date": "latest",
        "station": station_id,
        "product": product,
        "units": "english",
        "time_zone": "lst_ldt",
        "application": "NOS.COOPS.TAC.WL",
        "format": "json"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json()

def get_weather_data(station_id):
    try:
        # Fetch each product individually
        air_temp_data = fetch_product(station_id, "air_temperature")
        water_temp_data = fetch_product(station_id, "water_temperature")
        wind_data = fetch_product(station_id, "wind")

        # Extract relevant data
        air_temp = None
        water_temp = None
        wind_speed = None
        gust_speed = None

        if air_temp_data['data']:
            air_temp = air_temp_data['data'][0]['v']
        if water_temp_data['data']:
            water_temp = water_temp_data['data'][0]['v']
        if wind_data['data']:
            wind_speed = wind_data['data'][0]['s']
            gust_speed = wind_data['data'][0].get('g', None)

        return {
            'air_temperature': f"{air_temp} F",
            'water_temperature': f"{water_temp} F",
            'wind_speed': f"{wind_speed} MPH",
            'gust_speed': f"{gust_speed} MPH" if gust_speed else "N/A"
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return {"error": "Failed to fetch weather data"}
    except Exception as e:
        logging.error(f"Error processing weather data: {e}")
        return {"error": "Internal server error"}

