import csv
import os
from datetime import datetime
import requests

# Function to fetch weather data
def fetch_weather_data(api_key, location):
    url = "https://api.weatherstack.com/current"
    params = {
        "access_key": api_key,
        "query": location
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed for {location}:", e)
        return {}

# Function to write weather data to CSV
def write_to_csv(file_name, location, data):
    file_exists = os.path.isfile(file_name)

    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Write header if file doesn't exist
        if not file_exists:
            writer.writerow([
                "Date", "Time", "Location", "Temperature", "Wind Speed", 
                "Wind Degree", "Pressure", "Precipitation", "Weather Description",
                "Humidity", "Cloud Cover", "Feels Like", "UV Index"
            ])

        # Check current and other necessary keys exist in the response
        if "current" in data:
            current_time = datetime.now()
            date = current_time.strftime("%Y-%m-%d")
            time_str = current_time.strftime("%H:%M:%S")

            # Extract required info
            temperature = data['current']['temperature']
            wind_speed = data['current']['wind_speed']
            wind_degree = data['current']['wind_degree']
            pressure = data['current']['pressure']
            precip = data['current']['precip']
            weather_desc = data['current']['weather_descriptions'][0]
            humidity = data['current']['humidity']
            cloudcover = data['current']['cloudcover']
            feelslike = data['current']['feelslike']
            uv_index = data['current']['uv_index']

            # Write data row
            writer.writerow([
                date, time_str, location, temperature, wind_speed, wind_degree,
                pressure, precip, weather_desc, humidity, cloudcover, feelslike, uv_index
            ])
            print(f"Data for '{location}' written to CSV.")
        else:
            print(f"Error: Weather data not found for '{location}'. Response:", data)
