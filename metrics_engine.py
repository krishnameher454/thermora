import math

# ── Risk Tier Palette (Option A – Emergency Command Center) ───────────────────
RISK_TIERS = [
    (0,   26,  "Normal",           "#10b981"),
    (27,  32,  "Caution",          "#fcd34d"),
    (33,  38,  "Extreme Caution",  "#f59e0b"),
    (39,  45,  "Danger",           "#f97316"),
    (46,  999, "Extreme Danger",   "#ef4444"),
]

UTCI_TIERS = [
    (-999, 9,   "No Thermal Stress",     "#10b981"),
    (9,    26,  "Moderate Stress",       "#fcd34d"),
    (26,   32,  "Strong Stress",         "#f59e0b"),
    (32,   38,  "Very Strong Stress",    "#f97316"),
    (38,   999, "Extreme Stress",        "#ef4444"),
]

def classify_risk(value: float, metric: str = "HI") -> dict:
    tiers = UTCI_TIERS if metric == "UTCI" else RISK_TIERS
    for low, high, name, colour in tiers:
        if low <= value <= high:
            return {"tier": name, "colour": colour}
    return {"tier": "Unknown", "colour": "#ffffff"}

# ── Heat Index (NOAA Rothfusz) ────────────────────────────────────────────────
def calc_heat_index(temp_c: float, rh: float) -> float:
    T = temp_c * 9 / 5 + 32
    R = rh
    HI = (-42.379 + 2.04901523*T + 10.14333127*R
          - 0.22475541*T*R - 0.00683783*T**2
          - 0.05481717*R**2 + 0.00122874*T**2*R
          + 0.00085282*T*R**2 - 0.00000199*T**2*R**2)
    if R < 13 and 80 <= T <= 112:
        HI -= ((13 - R) / 4) * math.sqrt((17 - abs(T - 95)) / 17)
    elif R > 85 and 80 <= T <= 87:
        HI += ((R - 85) / 10) * ((87 - T) / 5)
    return round((HI - 32) * 5 / 9, 2)

# ── Wet-Bulb Temperature (Stull 2011) ────────────────────────────────────────
def _wet_bulb(temp_c: float, rh: float) -> float:
    T, R = temp_c, rh
    return (T * math.atan(0.151977 * math.sqrt(R + 8.313659))
            + math.atan(T + R)
            - math.atan(R - 1.676331)
            + 0.00391838 * R**1.5 * math.atan(0.023101 * R)
            - 4.686035)

# ── WBGT (Liljegren approximation) ───────────────────────────────────────────
def calc_wbgt(temp_c: float, rh: float, wind_kmh: float, solar_wm2: float) -> float:
    T_wb = _wet_bulb(temp_c, rh)
    T_g  = temp_c + 0.1 * (solar_wm2 / 1000)
    WBGT = 0.7 * T_wb + 0.2 * T_g + 0.1 * wind_kmh * 0.27778
    return round(WBGT, 2)

# ── UTCI (simplified polynomial approximation) ────────────────────────────────
def calc_utci(temp_c: float, rh: float, wind_kmh: float, solar_wm2: float) -> float:
    """
    Simplified UTCI approximation based on:
    Bröde et al. (2012) – A universal scale for the assessment of the outdoor
    thermal environment: the Universal Thermal Climate Index.
    Uses Tmrt estimated from solar radiation.
    """
    wind_ms = max(wind_kmh * 0.27778, 0.5)  # m/s, minimum 0.5
    # Mean radiant temperature approximation
    T_mrt = temp_c + 0.5 * (solar_wm2 / 100)
    # Water vapour pressure (hPa)
    e = (rh / 100) * 6.105 * math.exp(25.22 * (temp_c - 273.16) / temp_c - 5.31 * math.log(temp_c / 273.16))
    # Simplified UTCI polynomial (Fiala et al.)
    D_Tmrt = T_mrt - temp_c
    UTCI = (temp_c
            + 0.607562052
            - 0.0227712343 * temp_c
            + 8.06470461e-4 * temp_c**2
            - 1.54271797e-4 * temp_c**3
            + D_Tmrt * (0.0961509617 + 2.47805911e-4 * temp_c - 1.35769480e-4 * D_Tmrt)
            + wind_ms * (-2.25836520 + 0.0880326035 * temp_c + 0.00216844454 * D_Tmrt)
            + e * (0.348116035 - 0.00119279337 * temp_c + 0.000791207751 * D_Tmrt))
    return round(UTCI, 2)

# ── IMD Heatwave Definition ───────────────────────────────────────────────────
def imd_heatwave_check(temp_c: float, region: str = "plains", normal_temp: float = None) -> dict:
    """
    Check if conditions meet IMD heatwave criteria.
    region: 'plains', 'coastal', or 'hills'
    normal_temp: climatological normal for the location (optional)
    """
    thresholds = {"plains": 40, "coastal": 37, "hills": 30}
    threshold  = thresholds.get(region, 40)
    is_hw      = temp_c >= threshold
    severity   = "Normal"
    colour     = "#10b981"

    if is_hw:
        severity = "Heatwave"
        colour   = "#f97316"
        if normal_temp and (temp_c - normal_temp) >= 6.5:
            severity = "Severe Heatwave"
            colour   = "#ef4444"
        elif normal_temp and (temp_c - normal_temp) >= 4.5:
            severity = "Heatwave"
            colour   = "#f97316"

    return {
        "is_heatwave": is_hw,
        "severity": severity,
        "colour": colour,
        "threshold": threshold,
        "deviation": round(temp_c - normal_temp, 1) if normal_temp else None,
    }

# ── Age & Vulnerable Group Advisories ────────────────────────────────────────
ADVISORIES = {
    "child": {
        "Normal":           "Stay hydrated. Limit midday outdoor activity.",
        "Caution":          "Provide shaded areas, encourage frequent water intake.",
        "Extreme Caution":  "Reduce outdoor time significantly. Use cool, damp cloths.",
        "Danger":           "Keep child indoors. Watch for heat cramps and exhaustion.",
        "Extreme Danger":   "Do NOT go outside. Seek medical attention if heatstroke symptoms appear.",
    },
    "adult": {
        "Normal":           "Maintain regular hydration. Normal outdoor activity is fine.",
        "Caution":          "Take breaks in shade. Drink water every 30 minutes.",
        "Extreme Caution":  "Reduce strenuous activity. Wear light, loose clothing.",
        "Danger":           "Avoid outdoor work. Watch for dizziness, nausea, or rapid heartbeat.",
        "Extreme Danger":   "Emergency – seek air-conditioned shelter immediately. Call for help if symptoms occur.",
    },
    "elderly": {
        "Normal":           "Stay hydrated. Avoid midday sun (11 AM – 4 PM).",
        "Caution":          "Rest in air-conditioned or shaded spaces. Keep water nearby.",
        "Extreme Caution":  "Limit outdoor time. Use cooling cloths on neck and wrists.",
        "Danger":           "Stay indoors. Monitor blood pressure and medications.",
        "Extreme Danger":   "Immediate medical assistance if confusion, fainting, or seizures occur.",
    },
    "pregnant": {
        "Normal":           "Stay hydrated. Avoid direct sun for prolonged periods.",
        "Caution":          "Rest frequently. Drink at least 3 litres of water daily.",
        "Extreme Caution":  "Stay indoors during peak heat. Contact doctor if feeling unwell.",
        "Danger":           "Avoid all outdoor exposure. Monitor fetal movement and body temperature.",
        "Extreme Danger":   "Contact OB-GYN immediately. Heat stress can harm the fetus.",
    },
    "outdoor_worker": {
        "Normal":           "Take regular water breaks. Wear a hat and light clothing.",
        "Caution":          "Work in shade when possible. Hydrate every 20 minutes.",
        "Extreme Caution":  "Reschedule heavy work to early morning or evening. Wear cooling vests.",
        "Danger":           "Stop outdoor work. Rest in shade or indoors immediately.",
        "Extreme Danger":   "All outdoor work must STOP. Heat stroke risk is critical.",
    },
}

def get_advisory(age_group: str, risk_tier: str) -> str:
    group = ADVISORIES.get(age_group.lower())
    if not group:
        return "No advisory available for this group."
    return group.get(risk_tier, "Stay cautious and stay hydrated.")
