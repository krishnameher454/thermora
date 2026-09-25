import streamlit as st
import pandas as pd
import io

from header import render_header
from auth import login, logout, role_switcher
from weather_service import (
    get_current_weather, get_forecast, get_daily_forecast,
    search_location, INDIAN_CITIES
)
from metrics_engine import (
    calc_heat_index, calc_wbgt, calc_utci,
    classify_risk, imd_heatwave_check, get_advisory
)
from gauges import heat_index_gauge, wbgt_gauge, utci_gauge

st.set_page_config(
    page_title="THERMORA – SIH 2026 (MoES)",
    page_icon="🌡️",
    layout="wide",
)

render_header()

# ── Authentication ─────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in", False):
    st.sidebar.subheader("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Log in", use_container_width=True):
        if login(username, password):
            st.rerun()
        else:
            st.sidebar.error("Enter a valid username and password.")
    st.markdown("""
    <div style='text-align:center; margin-top:60px; color:#94a3b8;'>
        <h2 style='color:#ef4444;'>🌡️ THERMORA</h2>
        <p>Extreme Heatwave Early Warning System</p>
        <p style='font-size:0.85rem;'>Ministry of Earth Sciences (MoES) | SIH 2026</p>
        <p style='margin-top:30px;'>👈 Please log in from the sidebar to access the dashboard.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Sidebar: user info + role ──────────────────────────────────────────────────
st.sidebar.success(f"✅ Logged in as **{st.session_state.get('username', 'User')}**")
if st.sidebar.button("Log out", use_container_width=True):
    logout()
    st.rerun()

role_switcher()
role = st.session_state.get("role", "citizen")

# ── Sidebar: location ──────────────────────────────────────────────────────────
st.sidebar.subheader("📍 Location")
city_mode = st.sidebar.radio("Select mode", ["Quick pick (India)", "Search any city"])
lat, lon, city_name = 28.6139, 77.2090, "New Delhi"

if city_mode == "Quick pick (India)":
    city_names = [c["name"] for c in INDIAN_CITIES]
    sel = st.sidebar.selectbox("Choose city", city_names)
    city_obj = next(c for c in INDIAN_CITIES if c["name"] == sel)
    lat, lon, city_name = city_obj["latitude"], city_obj["longitude"], sel
else:
    query = st.sidebar.text_input("Type city name", value="New Delhi")
    if query:
        results = search_location(query)
        if results:
            opts = [f"{r['name']} ({r['latitude']:.2f}°, {r['longitude']:.2f}°)" for r in results]
            sel  = st.sidebar.selectbox("Results", opts)
            idx  = opts.index(sel)
            lat, lon = results[idx]["latitude"], results[idx]["longitude"]
            city_name = results[idx]["name"]
        else:
            st.sidebar.warning("No results – using New Delhi.")

# ── Sidebar: region type for IMD ───────────────────────────────────────────────
region = st.sidebar.selectbox("Region type (IMD)", ["plains", "coastal", "hills"], index=0)

# ── Fetch & calculate ──────────────────────────────────────────────────────────
weather  = get_current_weather(lat, lon)
temp     = weather.get("temperature", 38.0)
rh       = weather.get("relativehumidity", 50) or 50
wind     = weather.get("windspeed", 10.0) or 10.0
solar    = weather.get("solar_radiation", 700.0) or 700.0
hi       = calc_heat_index(temp, rh)
wbgt     = calc_wbgt(temp, rh, wind, solar)
utci     = calc_utci(temp, rh, wind, solar)
hi_risk  = classify_risk(hi)
wbgt_risk= classify_risk(wbgt)
utci_risk= classify_risk(utci, "UTCI")
imd      = imd_heatwave_check(temp, region)
is_fb    = weather.get("is_fallback", False)

if is_fb:
    st.warning("⚠️ Using offline demo data. Check your internet connection.")

# ── Heatwave banner ────────────────────────────────────────────────────────────
if imd["is_heatwave"]:
    st.markdown(
        f"<div style='background:{imd['colour']}22; border:2px solid {imd['colour']};"
        f"padding:14px; border-radius:10px; margin-bottom:16px; text-align:center;'>"
        f"<span style='color:{imd['colour']}; font-size:1.4rem; font-weight:bold;'>"
        f"🚨 IMD {imd['severity'].upper()} DECLARED – {city_name.upper()} | "
        f"Temp: {temp:.1f}°C (Threshold: {imd['threshold']}°C)</span></div>",
        unsafe_allow_html=True,
    )

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌡️ Live Monitor", "📈 Forecast", "💊 Advisory", "🗺️ Map", "👮 Officer Portal"
])

# ─────────────── TAB 1: LIVE MONITOR ─────────────────────────────────────────
with tab1:
    st.subheader(f"🌡️ Live Heat Stress – {city_name}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌡️ Temperature",      f"{temp:.1f} °C")
    c2.metric("💧 Humidity",          f"{rh} %")
    c3.metric("💨 Wind Speed",        f"{wind:.1f} km/h")
    c4.metric("☀️ Solar Radiation",   f"{solar:.0f} W/m²")

    st.divider()
    g1, g2, g3 = st.columns(3)
    with g1:  heat_index_gauge(hi)
    with g2:  wbgt_gauge(wbgt)
    with g3:  utci_gauge(utci)

    st.divider()
    # Risk summary table
    st.markdown("### 📊 Risk Summary")
    summary = pd.DataFrame([
        {"Index": "Heat Index (HI)",           "Value (°C)": hi,   "Risk Tier": hi_risk["tier"]},
        {"Index": "WBGT",                      "Value (°C)": wbgt, "Risk Tier": wbgt_risk["tier"]},
        {"Index": "UTCI",                      "Value (°C)": utci, "Risk Tier": utci_risk["tier"]},
        {"Index": "IMD Heatwave Status",       "Value (°C)": temp, "Risk Tier": imd["severity"]},
    ])
    st.dataframe(summary, use_container_width=True, hide_index=True)

    # Download button
    csv = summary.to_csv(index=False).encode()
    st.download_button("📥 Download Report (CSV)", data=csv,
                       file_name=f"thermora_{city_name}_{temp}C.csv",
                       mime="text/csv")

# ─────────────── TAB 2: FORECAST ─────────────────────────────────────────────
with tab2:
    st.subheader(f"📈 5-Day Forecast – {city_name}")
    daily = get_daily_forecast(lat, lon, days=5)
    if not daily.empty:
        for _, row in daily.iterrows():
            day_hi   = calc_heat_index(row["temp_max"], rh)
            day_risk = classify_risk(day_hi)
            colour   = day_risk["colour"]
            date_str = row["date"].strftime("%A, %d %b")
            st.markdown(
                f"<div style='background:#1e293b; border-left:5px solid {colour};"
                f"padding:12px 18px; border-radius:8px; margin-bottom:8px;"
                f"display:flex; justify-content:space-between;'>"
                f"<span style='color:#e5e7eb; font-size:1rem;'><b>{date_str}</b></span>"
                f"<span style='color:{colour}; font-size:1rem;'>"
                f"🌡️ Max: {row['temp_max']:.1f}°C &nbsp;|&nbsp; "
                f"HI: {day_hi:.1f}°C &nbsp;|&nbsp; "
                f"<b>{day_risk['tier']}</b></span></div>",
                unsafe_allow_html=True,
            )
        st.divider()
        st.line_chart(daily.set_index("date")[["temp_max", "wind_max"]])
        st.caption("Blue = Max Temperature (°C) | Orange = Max Wind Speed (km/h)")
    else:
        st.info("Forecast data unavailable. Check your internet connection.")

# ─────────────── TAB 3: ADVISORY ─────────────────────────────────────────────
with tab3:
    st.subheader("💊 Personalized Health Advisory")
    age_group = st.selectbox(
        "Select Group",
        ["adult", "child", "elderly", "pregnant", "outdoor_worker"],
        format_func=lambda x: {
            "adult": "👨 Adult",
            "child": "👧 Child",
            "elderly": "👴 Elderly",
            "pregnant": "🤰 Pregnant Woman",
            "outdoor_worker": "👷 Outdoor / Construction Worker",
        }[x]
    )
    advisory = get_advisory(age_group, hi_risk["tier"])
    colour   = hi_risk["colour"]
    st.markdown(
        f"<div style='background:#1e293b; border-left:6px solid {colour};"
        f"padding:20px; border-radius:10px;'>"
        f"<h3 style='color:{colour}; margin:0;'>🔔 {hi_risk['tier']}</h3>"
        f"<p style='color:#e5e7eb; font-size:1.1rem; margin-top:12px;'>{advisory}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("### 📋 General Heatwave Do's & Don'ts")
    col_do, col_dont = st.columns(2)
    with col_do:
        st.success("""
        **✅ DO:**
        - Drink water every 20-30 minutes
        - Wear light, loose, cotton clothes
        - Stay indoors between 11 AM – 4 PM
        - Use ORS if feeling dehydrated
        - Keep cool cloths on neck & forehead
        - Check on elderly neighbors
        """)
    with col_dont:
        st.error("""
        **❌ DON'T:**
        - Don't go out without a hat/umbrella
        - Don't drink alcohol or caffeinated drinks
        - Don't leave children/pets in parked cars
        - Don't do heavy physical work in peak heat
        - Don't ignore dizziness or confusion
        - Don't skip meals – eat light and frequent
        """)

# ─────────────── TAB 4: MAP ──────────────────────────────────────────────────
with tab4:
    st.subheader("🗺️ Geospatial Heat-Stress Map – India")
    try:
        from map_component import render_map
        render_map(lat, lon, city_name)
    except Exception as e:
        st.info(
            f"📍 **Selected:** {city_name} | Lat: {lat:.4f}° | Lon: {lon:.4f}°\n\n"
            f"Map could not render ({e}). Ensure `streamlit-folium` and `folium` are installed."
        )
    st.markdown("""
    <div style='background:#1e293b; padding:12px; border-radius:8px; margin-top:12px;'>
        <b style='color:#f59e0b;'>🗺️ Map Legend:</b>
        <span style='color:#10b981;'>🟢 Normal</span> &nbsp;|&nbsp;
        <span style='color:#fcd34d;'>🟡 Caution</span> &nbsp;|&nbsp;
        <span style='color:#f59e0b;'>🟠 Extreme Caution</span> &nbsp;|&nbsp;
        <span style='color:#f97316;'>🔴 Danger</span> &nbsp;|&nbsp;
        <span style='color:#ef4444;'>🆘 Extreme Danger</span>
    </div>
    """, unsafe_allow_html=True)

# ─────────────── TAB 5: OFFICER PORTAL ───────────────────────────────────────
with tab5:
    if role == "officer":
        st.subheader("👮 Disaster Officer Dashboard")
        st.success("✅ Officer access granted")

        # Current live metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Heat Index",   f"{hi:.1f} °C",   hi_risk["tier"])
        c2.metric("WBGT",         f"{wbgt:.1f} °C", wbgt_risk["tier"])
        c3.metric("UTCI",         f"{utci:.1f} °C", utci_risk["tier"])

        st.divider()

        # Alert management
        st.markdown("### 🚨 Active Alerts")
        if "alerts" not in st.session_state:
            st.session_state["alerts"] = []

        # Auto-create alert if heatwave
        if imd["is_heatwave"] and not any(a["location"] == city_name for a in st.session_state["alerts"]):
            st.session_state["alerts"].append({
                "location": city_name,
                "severity": imd["severity"],
                "message":  f"IMD {imd['severity']} at {city_name}. Temp: {temp:.1f}°C",
                "colour":   imd["colour"],
                "status":   "Active",
            })

        if st.session_state["alerts"]:
            for i, alert in enumerate(st.session_state["alerts"]):
                col_alert, col_btn = st.columns([5, 1])
                with col_alert:
                    st.markdown(
                        f"<div style='background:#1e293b; border:1px solid {alert['colour']};"
                        f"padding:12px; border-radius:8px;'>"
                        f"<b style='color:{alert['colour']};'>🚨 {alert['severity']}</b> – "
                        f"<span style='color:#e5e7eb;'>{alert['message']}</span></div>",
                        unsafe_allow_html=True,
                    )
                with col_btn:
                    if st.button("✅ Resolve", key=f"resolve_{i}"):
                        st.session_state["alerts"].pop(i)
                        st.rerun()
        else:
            st.info("No active alerts.")

        st.divider()

        # Create manual alert
        st.markdown("### ➕ Create New Alert")
        with st.form("new_alert"):
            a_loc  = st.text_input("Zone / Location", value=city_name)
            a_sev  = st.selectbox("Severity", ["Heatwave Watch", "Heatwave Warning", "Severe Heatwave"])
            a_msg  = st.text_area("Alert Message",
                                  value=f"Heatwave conditions expected in {city_name}. "
                                        f"Activate response teams and cooling centres.")
            if st.form_submit_button("🚨 Issue Alert"):
                st.session_state["alerts"].append({
                    "location": a_loc,
                    "severity": a_sev,
                    "message":  a_msg,
                    "colour":   "#ef4444",
                    "status":   "Active",
                })
                st.success(f"Alert issued for {a_loc}!")
                st.rerun()

        st.divider()

        # Recommended actions
        st.markdown("### 📋 Standard Operating Procedures")
        st.markdown(f"""
        Based on current **{hi_risk['tier']}** conditions in **{city_name}**:

        - Activate district-level **Heat Action Plan (HAP)**.
        - Open **cooling centres** at schools, community halls, railway stations.
        - Deploy **mobile medical units** in high-risk zones (slums, construction sites).
        - Issue **public advisory** via All India Radio, Doordarshan, SMS alerts.
        - Coordinate with **NDMA, SDMA, and local bodies** for resource mobilization.
        - Monitor **vulnerable populations** – elderly, children, outdoor workers.
        - Ensure **water availability** at public places and work sites.
        - Brief **health centres** on heatstroke first-aid protocols.
        """)

        # Export report
        report_data = {
            "Location": [city_name],
            "Temperature (°C)": [temp],
            "Humidity (%)": [rh],
            "Wind Speed (km/h)": [wind],
            "Heat Index (°C)": [hi],
            "Heat Index Risk": [hi_risk["tier"]],
            "WBGT (°C)": [wbgt],
            "WBGT Risk": [wbgt_risk["tier"]],
            "UTCI (°C)": [utci],
            "UTCI Risk": [utci_risk["tier"]],
            "IMD Status": [imd["severity"]],
        }
        df_report = pd.DataFrame(report_data)
        csv_report = df_report.to_csv(index=False).encode()
        st.download_button(
            "📥 Download Officer Report (CSV)",
            data=csv_report,
            file_name=f"officer_report_{city_name}.csv",
            mime="text/csv",
        )
    else:
        st.warning("🔒 This section is for Disaster Officers only.\n\n"
                   "Switch your **role** to **Officer** in the sidebar to access this dashboard.")
        st.markdown("""
        <div style='text-align:center; margin-top:40px; color:#94a3b8;'>
            <p>If you are a Disaster Officer, select <b>officer</b> from the role dropdown in the left sidebar.</p>
        </div>
        """, unsafe_allow_html=True)
