import requests
import pandas as pd
from datetime import datetime, timedelta

BASE_URL    = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"

FALLBACK_DATA = {
    "temperature": 42.0,
    "relativehumidity": 35,
    "windspeed": 12.0,
    "solar_radiation": 900.0,
    "time": datetime.utcnow().isoformat(),
    "is_fallback": True,
}

# 20 major Indian cities pre-loaded
INDIAN_CITIES = [
    {"name": "New Delhi",     "latitude": 28.6139,  "longitude": 77.2090},
    {"name": "Mumbai",        "latitude": 19.0760,  "longitude": 72.8777},
    {"name": "Chennai",       "latitude": 13.0827,  "longitude": 80.2707},
    {"name": "Kolkata",       "latitude": 22.5726,  "longitude": 88.3639},
    {"name": "Bengaluru",     "latitude": 12.9716,  "longitude": 77.5946},
    {"name": "Hyderabad",     "latitude": 17.3850,  "longitude": 78.4867},
    {"name": "Ahmedabad",     "latitude": 23.0225,  "longitude": 72.5714},
    {"name": "Pune",          "latitude": 18.5204,  "longitude": 73.8567},
    {"name": "Jaipur",        "latitude": 26.9124,  "longitude": 75.7873},
    {"name": "Lucknow",       "latitude": 26.8467,  "longitude": 80.9462},
    {"name": "Nagpur",        "latitude": 21.1458,  "longitude": 79.0882},
    {"name": "Bhopal",        "latitude": 23.2599,  "longitude": 77.4126},
    {"name": "Patna",         "latitude": 25.5941,  "longitude": 85.1376},
    {"name": "Bhubaneswar",   "latitude": 20.2961,  "longitude": 85.8245},
    {"name": "Chandigarh",    "latitude": 30.7333,  "longitude": 76.7794},
    {"name": "Coimbatore",    "latitude": 11.0168,  "longitude": 76.9558},
    {"name": "Surat",         "latitude": 21.1702,  "longitude": 72.8311},
    {"name": "Kanpur",        "latitude": 26.4499,  "longitude": 80.3319},
    {"name": "Visakhapatnam", "latitude": 17.6868,  "longitude": 83.2185},
    {"name": "Kochi",         "latitude": 9.9312,   "longitude": 76.2673},
]

def get_current_weather(lat: float, lon: float) -> dict:
    """Fetch current weather from Open-Meteo. Falls back to demo data on error."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "hourly": "relativehumidity_2m,shortwave_radiation",
        "timezone": "auto",
        "forecast_days": 1,
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        cur  = data.get("current_weather", {})
        t_iso = cur.get("time", "")
        hourly_times = data["hourly"]["time"]
        idx  = hourly_times.index(t_iso) if t_iso in hourly_times else -1
        rh   = data["hourly"]["relativehumidity_2m"][idx] if idx != -1 else 50
        solar= data["hourly"]["shortwave_radiation"][idx] if idx != -1 else 600
        return {
            "temperature":    cur.get("temperature", 35.0),
            "relativehumidity": rh,
            "windspeed":      cur.get("windspeed", 10.0),
            "solar_radiation": solar,
            "time":           t_iso,
            "is_fallback":    False,
        }
    except Exception:
        return FALLBACK_DATA

def get_forecast(lat: float, lon: float, days: int = 5) -> pd.DataFrame:
    """Return hourly forecast DataFrame for up to 5 days."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relativehumidity_2m,windspeed_10m,shortwave_radiation",
        "forecast_days": days,
        "timezone": "auto",
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame({
            "time":            pd.to_datetime(data["hourly"]["time"]),
            "temperature":     data["hourly"]["temperature_2m"],
            "relativehumidity":data["hourly"]["relativehumidity_2m"],
            "windspeed":       data["hourly"]["windspeed_10m"],
            "solar_radiation": data["hourly"]["shortwave_radiation"],
        })
        return df
    except Exception:
        return pd.DataFrame()

def get_daily_forecast(lat: float, lon: float, days: int = 5) -> pd.DataFrame:
    """Return daily max-temperature forecast for up to 5 days."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,precipitation_sum,windspeed_10m_max",
        "forecast_days": days,
        "timezone": "auto",
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame({
            "date":        pd.to_datetime(data["daily"]["time"]),
            "temp_max":    data["daily"]["temperature_2m_max"],
            "wind_max":    data["daily"]["windspeed_10m_max"],
            "precip":      data["daily"]["precipitation_sum"],
        })
        return df
    except Exception:
        return pd.DataFrame()

def search_location(query: str, limit: int = 5) -> list:
    """Geocoding search via Open-Meteo. Returns list of {name, latitude, longitude}."""
    params = {"name": query, "count": limit, "language": "en", "format": "json"}
    try:
        r = requests.get(GEOCODE_URL, params=params, timeout=10)
        r.raise_for_status()
        return [
            {"name": res["name"], "latitude": res["latitude"], "longitude": res["longitude"]}
            for res in r.json().get("results", [])
        ]
    except Exception:
        return []
