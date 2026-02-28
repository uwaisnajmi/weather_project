import requests
import pandas as pd
import json
import os 
from datetime import datetime

# variable
lat = 5.365
long = 100.5618
csv = "weather_history.csv"

def extract():
    """Fetch data from the api"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&current_weather=true"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"error: could not fetch data. Status code: {response.status_code}")
        return None 

def transform(raw_data):
    """cleans and reshape the raw json into a flat structure"""
    current = raw_data['current_weather']

    # select only relevant data 
    cleaned_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "temp_celcius": current['temperature'],
        "wind_speed": current['windspeed'],
        "weather_code": current['weathercode']
    
    }
    return cleaned_data

def load_to_csv(data_dict):
    """Saves the data to a csv file (temporary 'database' for now)"""
    df = pd.DataFrame([data_dict])

    file_exists = os.path.exists(csv)
    df.to_csv(csv, mode='a', index=False, header=not file_exists)
    print(f"Data successfully saved to {csv}")

raw_json = extract()

if raw_json:
        processed_row = transform(raw_json)
        load_to_csv(processed_row)



