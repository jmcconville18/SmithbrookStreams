import requests
import logging
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(level=logging.DEBUG)

WEATHER_API_KEY = '688e77c8723821db62ddccb30bfb7630'
FORECAST_API_URL = 'https://api.openweathermap.org/data/2.5/forecast'
GEOCODING_API_URL = 'http://api.openweathermap.org/geo/1.0/zip'

def fetch_forecast_data(zip_code='06033'):
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

        # Fetch forecast data from OpenWeatherMap API
        forecast_url = f"{FORECAST_API_URL}?lat={lat}&lon={lon}&units=imperial&appid={WEATHER_API_KEY}"
        logging.debug(f"Forecast API URL: {forecast_url}")
        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        logging.debug(f"Forecast Data: {forecast_data}")
        return {"data": format_forecast_data(forecast_data), "forecast_url": forecast_url, "geo_url": geo_url}

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return {"error": "Failed to fetch forecast data", "geo_url": geo_url}
    except Exception as e:
        logging.error(f"Error fetching forecast data: {e}")
        return {"error": "Failed to fetch forecast data", "geo_url": geo_url}

def format_forecast_data(data):
    from datetime import datetime

    days = defaultdict(lambda: {"high": float('-inf'), "low": float('inf'), "descriptions": [], "summary": []})

    for item in data['list']:
        dt = datetime.fromtimestamp(item['dt'])
        date = dt.strftime('%Y-%m-%d')
        time = dt.strftime('%I %p')

        if dt.hour in [2, 5, 23]:
            continue

        days[date]['high'] = max(days[date]['high'], item['main']['temp_max'])
        days[date]['low'] = min(days[date]['low'], item['main']['temp_min'])
        description = item['weather'][0]['description']
        days[date]['descriptions'].append(f"{time} - {description}")
        days[date]['summary'].append(description)

    formatted_data = {"5-Day Forecast": []}
    for date, info in days.items():
        daily_summary = create_daily_summary(info['summary'])

        formatted_data["5-Day Forecast"].append({
            "date": date,
            "high": f"{round(info['high'])} °F",
            "low": f"{round(info['low'])} °F",
            "descriptions": ", ".join(info['descriptions']),
            "DailySummary": daily_summary
        })

    return formatted_data

def create_daily_summary(summary_list):
    summary_counter = Counter(summary_list)
    most_common = summary_counter.most_common(3)
    
    summary_phrases = []
    for description, count in most_common:
        if 'rain' in description:
            summary_phrases.append('Showers')
        elif 'cloud' in description:
            if 'few clouds' in description or 'scattered clouds' in description:
                summary_phrases.append('Partly Cloudy')
            else:
                summary_phrases.append('Cloudy')
        elif 'clear' in description:
            summary_phrases.append('Clear')
        elif 'snow' in description:
            summary_phrases.append('Snow')
        elif 'thunderstorm' in description:
            summary_phrases.append('Thunderstorms')
        else:
            summary_phrases.append(description.capitalize())

    return ", ".join(summary_phrases)

