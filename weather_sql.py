import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
LAT = 1.55
LONG = 103.63

DB_CONFIG = {
    "dbname":   os.getenv("DB_NAME", "weather_db"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "0637"),
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     os.getenv("DB_PORT", 5432),
}

# --- Extract ---
def extract() -> dict | None:
    """Fetch current weather data from Open-Meteo API."""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LONG}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        f"precipitation,rain,wind_speed_10m,wind_direction_10m,"
        f"cloud_cover,surface_pressure,weather_code,is_day"
        f"&timezone=Asia%2FKuala_Lumpur"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[Extract] Error fetching data: {e}")
        return None

# --- Transform ---
def transform(raw_data: dict) -> dict | None:
    """Clean and reshape raw JSON into a flat structure."""
    try:
        c = raw_data["current"]
        return {
            "recorded_at":        c["time"],
            "temp_celsius":       c["temperature_2m"],
            "feels_like_celsius": c["apparent_temperature"],
            "humidity_pct":       c["relative_humidity_2m"],
            "precipitation_mm":   c["precipitation"],
            "rain_mm":            c["rain"],
            "wind_speed_kmh":     c["wind_speed_10m"],
            "wind_direction_deg": c["wind_direction_10m"],
            "cloud_cover_pct":    c["cloud_cover"],
            "pressure_hpa":       c["surface_pressure"],
            "weather_code":       c["weather_code"],
            "is_day":             bool(c["is_day"]),
        }
    except KeyError as e:
        print(f"[Transform] Missing key in API response: {e}")
        return None

# --- Load ---
def load_to_postgres(data: dict) -> None:
    """Insert a weather reading into PostgreSQL, skipping duplicates."""
    sql = """
        INSERT INTO weather_readings (
            recorded_at, temp_celsius, feels_like_celsius, humidity_pct,
            precipitation_mm, rain_mm, wind_speed_kmh, wind_direction_deg,
            cloud_cover_pct, pressure_hpa, weather_code, is_day
        ) VALUES (
            %(recorded_at)s, %(temp_celsius)s, %(feels_like_celsius)s, %(humidity_pct)s,
            %(precipitation_mm)s, %(rain_mm)s, %(wind_speed_kmh)s, %(wind_direction_deg)s,
            %(cloud_cover_pct)s, %(pressure_hpa)s, %(weather_code)s, %(is_day)s
        )
        ON CONFLICT (recorded_at) DO NOTHING;
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, data)
        print(f"[Load] Data saved for {data['recorded_at']}")
    except psycopg2.Error as e:
        print(f"[Load] Database error: {e}")

# --- Setup (run once) ---
def setup_database() -> None:
    """Create the weather_readings table if it doesn't exist."""
    sql = """
        CREATE TABLE IF NOT EXISTS weather_readings (
            id                  SERIAL PRIMARY KEY,
            recorded_at         TIMESTAMP WITH TIME ZONE NOT NULL,

            temp_celsius        NUMERIC(5,2),
            feels_like_celsius  NUMERIC(5,2),

            humidity_pct        NUMERIC(5,2),
            precipitation_mm    NUMERIC(6,2),
            rain_mm             NUMERIC(6,2),

            wind_speed_kmh      NUMERIC(5,2),
            wind_direction_deg  SMALLINT,

            cloud_cover_pct     SMALLINT,
            pressure_hpa        NUMERIC(7,2),

            weather_code        SMALLINT,
            is_day              BOOLEAN,

            UNIQUE (recorded_at)
        );

        CREATE INDEX IF NOT EXISTS idx_weather_recorded_at
            ON weather_readings (recorded_at DESC);
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
        print("[Setup] Table ready.")
    except psycopg2.Error as e:
        print(f"[Setup] Failed to create table: {e}")

# --- Main ---
if __name__ == "__main__":
    setup_database()

    raw_json = extract()
    if raw_json:
        processed_row = transform(raw_json)
        if processed_row:
            load_to_postgres(processed_row)