import os
import requests
from dotenv import load_dotenv

load_dotenv()


# Gets latitude and longitude for a city name
# OpenWeather needs lat/lon instead of city name for AQI calls
def get_coordinates(city):
    # Reject fake city names
    cleaned = city.strip().lower()
    if len(cleaned) < 3:
        return None, None

    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"

    data = request_json(url)
    error_message = get_error_message(data)
    if error_message:
        print(f"Geo lookup error: {error_message}")
        return None, None

    # If city not found or response is not a list, return None
    if not isinstance(data, list) or not data:
        return None, None

    # After getting data from API, check the name matches
    returned = data[0].get("name", "").lower()
    if cleaned not in returned and returned not in cleaned:
        return None, None

    return data[0]["lat"], data[0]["lon"]


# Call an OpenWeather endpoint and return JSON safely.
def request_json(url):
    try:
        response = requests.get(url, timeout=12)
        return response.json()
    except requests.RequestException as error:
        print(f"Request failed: {error}")
        return {"message": "Network error"}


# Extract an error message from an OpenWeather response if present.
def get_error_message(data):
    if isinstance(data, dict):
        message = data.get("message")
        if message:
            return message
    return ""


# Return the first item of a list field safely.
def get_first_list_item(data, key):
    items = data.get(key, [])
    if not items:
        return None
    return items[0]


# Pull the main and wind blocks from the weather response safely.
def get_weather_blocks(weather_response):
    main_block = weather_response.get("main")
    wind_block = weather_response.get("wind")
    if not main_block or not wind_block:
        return None, None
    return main_block, wind_block


# Build a standard error response dictionary.
def build_error(message):
    return {"error": message}


# Return the EPA breakpoint table for PM2.5 AQI calculation.
def get_pm25_breakpoints():
    return [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500),
    ]


# Converts PM2.5 value to standard AQI number
# This is the official US EPA formula used worldwide
def calculate_aqi_from_pm25(pm25):
    breakpoints = get_pm25_breakpoints()

    for pm_low, pm_high, aqi_low, aqi_high in breakpoints:
        if pm_low <= pm25 <= pm_high:
            # Official EPA formula
            aqi = ((aqi_high - aqi_low) / (pm_high - pm_low)) * (pm25 - pm_low) + aqi_low
            return round(aqi)

    return 500  # if extremely high


# Main function -- fetches AQI + weather for a city
# Returns a clean dictionary with all values we need
def fetch_aqi_data(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return build_error("OpenWeather API key missing")

    # Step 1 -- convert city name to coordinates
    lat, lon = get_coordinates(city)

    if not lat:
        return build_error(f"City '{city}' not found")

    # Step 2 -- fetch AQI data using coordinates
    aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    aqi_response = request_json(aqi_url)
    error_message = get_error_message(aqi_response)
    if error_message:
        return build_error(f"AQI request failed: {error_message}")

    # Step 3 -- fetch weather data using coordinates
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    weather_response = request_json(weather_url)
    error_message = get_error_message(weather_response)
    if error_message:
        return build_error(f"Weather request failed: {error_message}")

    # Step 4 -- pull out the exact values we need
    aqi_item = get_first_list_item(aqi_response, "list")
    if not aqi_item:
        return build_error("AQI data not available")

    components = aqi_item.get("components")
    if not components:
        return build_error("AQI components missing")
    main_block, wind_block = get_weather_blocks(weather_response)
    if not main_block or not wind_block:
        return build_error("Weather data not available")

    # Calculate a real AQI from PM2.5 value
    # PM2.5 is the most accurate way to calculate AQI
    from datetime import datetime
    pm25 = round(components.get("pm2_5", 0), 1)
    aqi = calculate_aqi_from_pm25(pm25)
    current_hour = datetime.now().hour
    time_of_day = (
        "early morning" if current_hour < 7 else
        "morning" if current_hour < 12 else
        "afternoon" if current_hour < 17 else
        "evening" if current_hour < 20 else
        "night"
    )

    return {
        "city": city,
        "aqi": aqi,
        "pm25": pm25,
        "pm10": round(components.get("pm10", 0), 1),
        "co": round(components.get("co", 0), 1),
        "temperature": round(main_block.get("temp", 0), 1),
        "humidity": main_block.get("humidity", 0),
        "wind_speed": round(wind_block.get("speed", 0), 1),
        "time_of_day": time_of_day,
    }
