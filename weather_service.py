import requests
import pandas as pd
from datetime import datetime, timedelta

BASE_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"

# Simple fallback data for offline demo (danger scenario)
FALLBACK_DATA = {
    "temperature": 40.0,  # Celsius
    "relativehumidity": 80,  # percent
    "windspeed": 10.0,  # km/h
    "solar_radiation": 900.0,  # W/m^2
    "time": datetime.utcnow().isoformat()
}

def _request(params: dict) -> dict:
    """Internal helper to perform GET request and return JSON.
    Raises a RuntimeError on failure.
    """
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise RuntimeError(f"Open-Meteo request failed: {e}")

def get_current_weather(lat: float, lon: float) -> dict:
    """Fetch current weather for given latitude/longitude.
    Returns a dict with keys: temperature, relativehumidity, windspeed, solar_radiation, time.
    If the API fails, returns FALLBACK_DATA.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "hourly": "relativehumidity_2m,solar_radiation",
        "timezone": "UTC",
    }
    try:
        data = _request(params)
        cur = data.get("current_weather", {})
        time_iso = cur.get("time")
        hourly_time = data["hourly"]["time"]
        idx = hourly_time.index(time_iso) if time_iso in hourly_time else -1
        rh = data["hourly"]["relativehumidity_2m"][idx] if idx != -1 else None
        solar = data["hourly"]["solar_radiation"][idx] if idx != -1 else None
        return {
            "temperature": cur.get("temperature"),
            "relativehumidity": rh,
            "windspeed": cur.get("windspeed"),
            "solar_radiation": solar,
            "time": time_iso,
        }
    except Exception:
        return FALLBACK_DATA

def get_forecast(lat: float, lon: float, days: int = 3) -> pd.DataFrame:
    """Return a DataFrame with hourly forecast for the next `days` days.
    Columns: time, temperature, relativehumidity, windspeed, solar_radiation.
    """
    end_date = (datetime.utcnow() + timedelta(days=days)).date().isoformat()
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relativehumidity_2m,windspeed_10m,solar_radiation",
        "start_date": datetime.utcnow().date().isoformat(),
        "end_date": end_date,
        "timezone": "UTC",
    }
    data = _request(params)
    df = pd.DataFrame({
        "time": pd.to_datetime(data["hourly"]["time"]),
        "temperature": data["hourly"]["temperature_2m"],
        "relativehumidity": data["hourly"]["relativehumidity_2m"],
        "windspeed": data["hourly"]["windspeed_10m"],
        "solar_radiation": data["hourly"]["solar_radiation"],
    })
    return df

def search_location(query: str, limit: int = 5) -> list:
    """Search for locations using Open-Meteo geocoding API.
    Returns a list of dicts with `name`, `latitude`, `longitude`.
    """
    params = {"name": query, "count": limit, "language": "en", "format": "json"}
    try:
        resp = requests.get(GEOCODE_URL, params=params, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return [{"name": r["name"], "latitude": r["latitude"], "longitude": r["longitude"]} for r in results]
    except Exception:
        return []
