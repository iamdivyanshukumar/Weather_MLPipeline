import time
import os
import schedule
import requests
import pandas as pd
import joblib
import mysql.connector
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import OrdinalEncoder, StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from database import save_weather_to_sql
from weather_fetcher import fetch_weather_data, write_to_csv

# Configuration
API_KEY = "Your API Key"  # Your API key 
DB_CONFIG = {
    "host": "localhost",        # Save at local 
    "user": "root",
    "password": "***********",  # Replace with your MySQL password
    "database": "weather"
}
LOCATIONS = [
    "Hyderabad", "Ahmedabad", "Pune", "Jaipur", "Lucknow",
    "Patna", "Bhopal", "Surat", "Visakhapatnam", "Chandigarh",
    "Coimbatore", "Guwahati", "Thiruvananthapuram", "Indore", "Nagpur",
    "Vadodara", "Ludhiana", "Agra", "Nashik", "Meerut",
    "Rajkot", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad",
    "Amritsar", "Allahabad", "Jodhpur", "Ranchi", "Madurai"
]
CSV_FILE = "weather_data.csv"
MODEL_PATH = "model.joblib"
ACCURACY_PATH = "model_accuracy.txt"
INTERVAL = 5 * 24 * 60 * 60  # 5 days in seconds


# 1. Fetch and Save Weather Data 
def fetch_and_save_weather():
    for location in LOCATIONS:
        print(f"Fetching weather data for: {location}")
        weather_data = fetch_weather_data(API_KEY, location)

        if weather_data:
            write_to_csv(CSV_FILE, location, weather_data)
            save_weather_to_sql(location, weather_data)
        else:
            print(f"Failed to fetch data for '{location}'.")


# 2. Data Preprocessing
def preprocess_data():
    connection = mysql.connector.connect(**DB_CONFIG)
    query = """
    SELECT location, temperature, wind_speed, wind_degree, pressure, precipitation,
           weather_description, humidity, cloud_cover, feels_like, uv_index
    FROM weather_data
    """
    df = pd.read_sql(query, connection)
    connection.close()

    # Drop missing values , this is because this is no missing values in the data till now
    df = df.dropna()

    # Odinal ecoding to transform the catagorical data for X
    encoder = OrdinalEncoder()
    # To balance the data 
    scaler = StandardScaler()
    # Label ecoding to transform the catagorical data for y
    label_encoder = LabelEncoder()

    df['location'] = encoder.fit_transform(df[['location']])
    
    columns_to_scale = ['temperature', 'wind_speed', 'wind_degree', 'pressure', 'precipitation',
                        'humidity', 'cloud_cover', 'feels_like', 'uv_index']
    
    df[columns_to_scale] = scaler.fit_transform(df[columns_to_scale])
    
    df['weather_description'] = label_encoder.fit_transform(df['weather_description'])

    X = df.drop('weather_description', axis=1)
    y = df['weather_description']
    return train_test_split(X, y, test_size=0.2, random_state=4)


# 3. Model training
def train_model():
    print("Starting model training...")
    X_train, X_test, y_train, y_test = preprocess_data()

    model = GaussianNB()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.2f}")
    print(classification_report(y_test, y_pred))

    save_model(model, accuracy)


def save_model(model, accuracy):
    # Check paths for saving the model and accuracy exist or not
    if not os.path.exists(MODEL_PATH) or not os.path.exists(ACCURACY_PATH):
        print("Saving the first model...")
        joblib.dump(model, MODEL_PATH)
        with open(ACCURACY_PATH, "w") as f:
            f.write(str(accuracy))
            
    # If file already exist
    else:
        with open(ACCURACY_PATH, "r") as f:
            current_accuracy = float(f.read())
        if accuracy > current_accuracy:
            print("New model performs better. Saving updated model...")
            joblib.dump(model, MODEL_PATH)
            with open(ACCURACY_PATH, "w") as f:
                f.write(str(accuracy))


#  4. Main Function
def main():
    while True:
        print("Step 1: Fetching and saving weather data...")
        fetch_and_save_weather()
        print("Fetching and saving is DONE")
        
        print("Step 2: Preprocessing data...")
        preprocess_data()  # Preprocessing immediately after fetching new data
        print("Preprocessing is DONE")
        
        print("Step 3: Training the model...")
        train_model()  # Train the model after preprocessing
        print("Model training is DONE")
        
        print(f"Sleeping for {INTERVAL} seconds (5 days)...")
        time.sleep(INTERVAL)  # Sleep after completing all tasks for a fixed interval(5 Days)


if __name__ == "__main__":
    main()
