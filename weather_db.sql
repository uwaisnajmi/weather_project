
-- Create the main table
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

-- Create index for fast time-based queries
CREATE INDEX IF NOT EXISTS idx_weather_recorded_at
    ON weather_readings (recorded_at DESC);