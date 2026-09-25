import math
import numpy as np

# Risk tier definitions for Option A dark theme (hex colours)
RISK_TIERS = [
    (0, 26, "Normal", "#10b981"),          # Green
    (27, 32, "Caution", "#fcd34d"),        # Yellow
    (33, 38, "Extreme Caution", "#f59e0b"),# Amber
    (39, 45, "Danger", "#f97316"),        # Orange
    (46, float('inf'), "Extreme Danger", "#ef4444"), # Red
]

def _risk_lookup(value: float) -> tuple:
    """Return (tier_name, colour) for a given metric value.
    Used for both Heat Index and WBGT.
    """
    for low, high, name, colour in RISK_TIERS:
        if low <= value <= high:
            return name, colour
    return "Unknown", "#ffffff"

def classify_risk(value: float, metric: str = "HI") -> dict:
    """Classify risk tier for a metric.
    Returns a dict with keys: tier, colour.
    """
    tier, colour = _risk_lookup(value)
    return {"tier": tier, "colour": colour}

def calc_heat_index(temp_c: float, rh: float) -> float:
    """Calculate Heat Index (HI) using NOAA Rothfusz formula.
    Input temperature in Celsius and relative humidity in percent.
    Returns Heat Index in Celsius.
    """
    # Convert to Fahrenheit for the formula
    T = temp_c * 9/5 + 32
    R = rh
    # Simple approximation for T >= 80°F and RH >= 40%
    HI_f = -42.379 + 2.04901523*T + 10.14333127*R - 0.22475541*T*R \
           - 0.00683783*T**2 - 0.05481717*R**2 + 0.00122874*T**2*R \
           + 0.00085282*T*R**2 - 0.00000199*T**2*R**2
    # Adjustments for low humidity or extreme heat
    if R < 13 and 80 <= T <= 112:
        adj = ((13 - R)/4) * math.sqrt((17 - abs(T - 95))/17)
        HI_f -= adj
    elif R > 85 and 80 <= T <= 87:
        adj = ((R - 85)/10) * ((87 - T)/5)
        HI_f += adj
    # Convert back to Celsius
    HI_c = (HI_f - 32) * 5/9
    return round(HI_c, 2)

def _wet_bulb_temperature(temp_c: float, rh: float) -> float:
    """Approximate wet‑bulb temperature using Stull's formula.
    Returns temperature in Celsius.
    """
    T = temp_c
    R = rh
    Tw = T * math.atan(0.151977 * math.sqrt(R + 8.313659)) \
         + math.atan(T + R) - math.atan(R - 1.676331) \
         + 0.00391838 * R**1.5 * math.atan(0.023101 * R) \
         - 4.686035
    return Tw

def calc_wbgt(temp_c: float, rh: float, wind_kmh: float, solar_wm2: float) -> float:
    """Calculate approximate Wet‑Bulb Globe Temperature (WBGT).
    Uses Stull wet‑bulb estimate, simple globe temperature, and wind speed.
    Returns WBGT in Celsius.
    """
    T_wb = _wet_bulb_temperature(temp_c, rh)
    # Approximate globe temperature: add a fraction of solar radiation
    T_g = temp_c + 0.1 * (solar_wm2 / 1000)  # solar in W/m2
    # Convert wind km/h to m/s (1 km/h = 0.27778 m/s) – factor not crucial for approximation
    WBGT = 0.7 * T_wb + 0.2 * T_g + 0.1 * wind_kmh * 0.27778
    return round(WBGT, 2)

# Age‑group advisory dictionary (example values)
ADVISORIES = {
    "child": {
        "Normal": "Stay hydrated and limit outdoor activity during peak sun hours.",
        "Caution": "Provide shaded area, encourage frequent water intake.",
        "Extreme Caution": "Limit outdoor exposure, consider indoor activities.",
        "Danger": "Keep child indoors, monitor for heat‑related illness.",
        "Extreme Danger": "Seek medical attention if signs of heatstroke appear."
    },
    "adult": {
        "Normal": "Maintain regular hydration and normal activity.",
        "Caution": "Take breaks in shade, drink water regularly.",
        "Extreme Caution": "Reduce strenuous activity, stay cool.",
        "Danger": "Avoid outdoor work, watch for dizziness or nausea.",
        "Extreme Danger": "Emergency – call for medical help if heatstroke symptoms occur."
    },
    "elderly": {
        "Normal": "Stay hydrated, avoid midday sun.",
        "Caution": "Rest in air‑conditioned spaces, keep water handy.",
        "Extreme Caution": "Limit outdoor time, use cooling cloths.",
        "Danger": "Stay indoors, monitor vitals, ensure medication compliance.",
        "Extreme Danger": "Immediate medical assistance required."
    }
}

def get_advisory(age_group: str, risk_tier: str) -> str:
    """Return advisory text for a given age group and risk tier.
    ``age_group`` should be one of "child", "adult", "elderly".
    ``risk_tier`` matches the tier names from ``classify_risk``.
    """
    group = ADVISORIES.get(age_group.lower())
    if not group:
        return "No advisory available for this age group."
    return group.get(risk_tier, "No specific advisory for this risk level.")
