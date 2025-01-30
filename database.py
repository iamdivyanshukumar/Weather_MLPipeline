import mysql.connector
from datetime import datetime

def save_weather_to_sql(location, data):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Divyanshu56@#",  # Replace with your MySQL password
        database="weather"
    )
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        date DATE,
        time TIME,
        location VARCHAR(255),
        temperature FLOAT,
        wind_speed FLOAT,
        wind_degree INT,
        pressure FLOAT,
        precipitation FLOAT,
        weather_description VARCHAR(255),
        humidity INT,
        cloud_cover INT,
        feels_like FLOAT,
        uv_index INT
    )""")

    if "current" in data:
        current_time = datetime.now()
        date = current_time.strftime("%Y-%m-%d")
        time_str = current_time.strftime("%H:%M:%S")

        cursor.execute("""
        INSERT INTO weather_data (date, time, location, temperature, wind_speed, wind_degree,
                                  pressure, precipitation, weather_description, humidity,
                                  cloud_cover, feels_like, uv_index)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            date, time_str, location,
            data['current']['temperature'],
            data['current']['wind_speed'],
            data['current']['wind_degree'],
            data['current']['pressure'],
            data['current']['precip'],
            data['current']['weather_descriptions'][0],
            data['current']['humidity'],
            data['current']['cloudcover'],
            data['current']['feelslike'],
            data['current']['uv_index']
        ))

    connection.commit()
    connection.close()
    print(f"Weather data for '{location}' saved to MySQL database.")
