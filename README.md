# 🌦️ Weather Pipeline

An automated ETL (Extract, Transform, Load) pipeline that collects real-time weather data for **Kulim, Kedah** every 15 minutes and stores it in a PostgreSQL database — fully containerized with Docker.

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Docker Compose                       │
│                                                         │
│  ┌──────────────────┐         ┌──────────────────────┐  │
│  │   ETL Container  │         │    DB Container      │  │
│  │                  │         │                      │  │
│  │  ┌────────────┐  │         │  ┌────────────────┐  │  │
│  │  │  Extract   │  │         │  │   PostgreSQL   │  │  │
│  │  │            │  │         │  │                │  │  │
│  │  │ Open-Meteo │  │         │  │ weather_       │  │  │
│  │  │    API     │  │         │  │ readings table │  │  │
│  │  └─────┬──────┘  │         │  └───────▲────────┘  │  │
│  │        │         │         │          │            │  │
│  │  ┌─────▼──────┐  │         │          │            │  │
│  │  │ Transform  │  │         │          │            │  │
│  │  │            │  │         │          │            │  │
│  │  │ Flatten &  │  │         │          │            │  │
│  │  │ Type cast  │  │         │          │            │  │
│  │  └─────┬──────┘  │         │          │            │  │
│  │        │         │         │          │            │  │
│  │  ┌─────▼──────┐  │  psycopg2  ┌──────┴─────────┐  │  │
│  │  │    Load    │◄─┼────────────►    port 5432    │  │  │
│  │  │            │  │         │  └────────────────┘  │  │
│  │  │  INSERT ON │  │         │                      │  │
│  │  │  CONFLICT  │  │         │                      │  │
│  │  │  DO NOTHING│  │         │                      │  │
│  │  └────────────┘  │         │                      │  │
│  │                  │         │                      │  │
│  │  ⏱ Runs every   │         │  💾 Data persisted   │  │
│  │    15 minutes    │         │     in Docker volume │  │
│  └──────────────────┘         └──────────────────────┘  │
└─────────────────────────────────────────────────────────┘

External:  Open-Meteo API (free, no API key required)
           └── https://api.open-meteo.com
```

---

## ✨ Features

- Fetches 11 weather metrics including temperature, humidity, wind, rain, and cloud cover
- Deduplicates records automatically: safe to re-run without creating duplicate rows
- Fully containerized: runs anywhere Docker is installed
- No API key required (uses the free [Open-Meteo](https://open-meteo.com/) API)
- Data persists across container restarts via Docker volumes

---

## 🗄️ Data Collected

| Column | Description | Unit |
|---|---|---|
| `recorded_at` | Timestamp of the reading | UTC+8 (KL) |
| `temp_celsius` | Air temperature | °C |
| `feels_like_celsius` | Apparent temperature | °C |
| `humidity_pct` | Relative humidity | % |
| `precipitation_mm` | Total precipitation | mm |
| `rain_mm` | Rainfall specifically | mm |
| `wind_speed_kmh` | Wind speed at 10m height | km/h |
| `wind_direction_deg` | Wind direction | degrees |
| `cloud_cover_pct` | Cloud coverage | % |
| `pressure_hpa` | Atmospheric pressure | hPa |
| `weather_code` | WMO weather code | — |
| `is_day` | Day or night flag | boolean |

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed
- That's it!

### 1. Clone the repository

```bash
git clone https://github.com/uwaisnajmi/weather_pipeline.git
cd weather_pipeline
```

### 2. Set up your environment variables

```bash
cp _env .env
```

Open `.env` and fill in your database password:

```env
DB_NAME=weather_db
DB_USER=postgres
DB_PASSWORD=0637
DB_HOST=localhost
DB_PORT=5432
```

> ⚠️ Never commit your `.env` file. It's already in `.gitignore`.

### 3. Run the pipeline

```bash
docker compose up -d
```

That's it! The pipeline will:
1. Start a PostgreSQL database
2. Create the `weather_readings` table automatically
3. Fetch and store weather data every 15 minutes

### 4. Query your data

Connect to the database using any PostgreSQL client (e.g. [DBeaver](https://dbeaver.io/), [TablePlus](https://tableplus.com/), or `psql`):

```
Host:     localhost
Port:     5433
Database: weather_db
User:     postgres
Password: 0637
```

```sql
-- See the latest 10 readings
SELECT recorded_at, temp_celsius, humidity_pct, weather_code
FROM weather_readings
ORDER BY recorded_at DESC
LIMIT 10;

-- Average temperature by day
SELECT DATE(recorded_at) AS day, ROUND(AVG(temp_celsius), 2) AS avg_temp
FROM weather_readings
GROUP BY day
ORDER BY day DESC;
```

### 5. Stop the pipeline

```bash
docker compose down        # stops containers, keeps data
docker compose down -v     # stops containers AND deletes all data
```

---

## 📁 Project Structure

```
weather-pipeline/
├── weather_sql.py        # Main ETL script (Extract → Transform → Load)
├── weather_db.sql        # Database schema (table + index definitions)
├── docker-compose.yml    # Container orchestration
├── requirements.txt      # Python dependencies
├── _env                  # Environment variable template
└── README.md
```

---

## 🔧 Tech Stack

| Tool | Purpose |
|---|---|
| Python 3 | ETL scripting |
| PostgreSQL 16 | Data storage |
| psycopg2 | Python → PostgreSQL connector |
| Open-Meteo API | Free weather data source |
| Docker & Compose | Containerization & orchestration |

---

## 🗺️ Roadmap

- [ ] Migrate scheduler to **Apache Airflow** for proper DAG-based orchestration

---
