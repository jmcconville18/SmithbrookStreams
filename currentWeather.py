import requests
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

WEATHER_API_KEY = '688e77c8723821db62ddccb30bfb7630'
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'
GEOCODING_API_URL = 'http://api.openweathermap.org/geo/1.0/zip'

def fetch_weather_data(zip_code='06033'):
    try:
        # Get lat and lon from OpenWeatherMap Geocoding API
        geo_url = f"{GEOCODING_API_URL}?zip={zip_code},US&appid={WEATHER_API_KEY}"
        geo_response = requests.get(geo_url)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        if not geo_data or 'lat' not in geo_data or 'lon' not in geo_data:
            logging.error("Invalid ZIP code or location not found.")
            return {"error": "Invalid ZIP code or location not found.", "geo_url": geo_url}

        lat, lon = geo_data['lat'], geo_data['lon']
        logging.debug(f"Latitude: {lat}, Longitude: {lon}")

        # Fetch weather data from OpenWeatherMap API
        weather_url = f"{WEATHER_API_URL}?lat={lat}&lon={lon}&units=imperial&appid={WEATHER_API_KEY}"
        logging.debug(f"Weather API URL: {weather_url}")
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        logging.debug(f"Weather Data: {weather_data}")
        return {"data": format_weather_data(weather_data), "weather_url": weather_url, "geo_url": geo_url}

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return {"error": "Failed to fetch weather data", "geo_url": geo_url}
    except Exception as e:
        logging.error(f"Error fetching weather data: {e}")
        return {"error": "Failed to fetch weather data", "geo_url": geo_url}

def format_weather_data(data):
    formatted_data = {
        "Temperature": f"{round(data['main']['temp'])} °F",
        "Feels Like": f"{round(data['main']['feels_like'])} °F",
        "Minimum Temperature": f"{round(data['main']['temp_min'])} °F",
        "Maximum Temperature": f"{round(data['main']['temp_max'])} °F",
        "Pressure": f"{data['main']['pressure']} hPa",
        "Humidity": f"{data['main']['humidity']} %",
        "Visibility": f"{(data['visibility'] / 1609.34):.2f} miles" if 'visibility' in data else 'N/A',
        "Wind Speed": f"{data['wind']['speed']} mph" if 'wind' in data else 'N/A',
        "Wind Gust": f"{data['wind'].get('gust', 'N/A')} mph",
        "Wind Direction": f"{data['wind']['deg']}°" if 'wind' in data else 'N/A',
        "Cloudiness": f"{data['clouds']['all']} %" if 'clouds' in data else 'N/A',
        "Rain (last hour)": f"{(data.get('rain', {}).get('1h', 0) / 25.4):.2f} inches",
        "Snow (last hour)": f"{(data.get('snow', {}).get('1h', 0) / 25.4):.2f} inches",
        "Weather": data['weather'][0]['description'] if 'weather' in data else 'N/A',
        "Sunrise": format_time(data['sys']['sunrise'], data['timezone']),
        "Sunset": format_time(data['sys']['sunset'], data['timezone']),
        "Time of Data Calculation": format_time(data['dt'], data['timezone'])
    }
    return formatted_data

def format_time(timestamp, timezone_offset):
    from datetime import datetime, timedelta
    utc_time = datetime.utcfromtimestamp(timestamp)
    local_time = utc_time + timedelta(seconds=timezone_offset)
    return local_time.strftime('%Y-%m-%d %H:%M:%S')

