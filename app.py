import streamlit as st
from datetime import datetime

# Local imports
from auth import login, logout, role_switcher
from weather_service import get_current_weather, get_forecast, search_location
from metrics_engine import calc_heat_index, calc_wbgt, classify_risk, get_advisory
from components.header import render_header
from components.gauges import heat_index_gauge, wbgt_gauge

# Page configuration (dark theme background set via CSS in header)
st.set_page_config(page_title="HeatAlert – SIH 2026 (MoES)", layout="wide")

# Render header (includes custom CSS for Option A dark theme)
render_header()

# Authentication UI (simple placeholder)
if not st.session_state.get('logged_in', False):
    st.sidebar.subheader('Login')
    username = st.sidebar.text_input('Username')
    password = st.sidebar.text_input('Password', type='password')
    if st.sidebar.button('Log in'):
        if login(username, password):
            st.sidebar.success('Logged in as ' + username)
        else:
            st.sidebar.error('Login failed')
    st.stop()
else:
    st.sidebar.subheader(f"Welcome, {st.session_state.get('username', 'User')}")
    if st.sidebar.button('Log out'):
        logout()
        st.experimental_rerun()

# Role selector (citizen/officer)
role_switcher()
role = st.session_state['role']

# Sidebar location search
st.sidebar.subheader('Location')
location_query = st.sidebar.text_input('Search place', value='New Delhi')
location_results = []
if location_query:
    location_results = search_location(location_query)
    if location_results:
        selected = st.sidebar.selectbox('Select', [f"{r['name']} ({r['latitude']:.2f}, {r['longitude']:.2f})" for r in location_results])
        idx = [i for i, r in enumerate(location_results) if f"{r['name']} ({r['latitude']:.2f}, {r['longitude']:.2f})" == selected][0]
        lat = location_results[idx]['latitude']
        lon = location_results[idx]['longitude']
    else:
        st.sidebar.warning('No results found, using default coordinates.')
        lat, lon = 28.6139, 77.2090  # New Delhi
else:
    lat, lon = 28.6139, 77.2090

# Main content tabs
tabs = st.tabs(["Live Monitor", "Forecast", "Advisory", "Map", "Officer Portal"])

# Live Monitor tab
with tabs[0]:
    st.header('Live Weather & Heat Stress')
    weather = get_current_weather(lat, lon)
    if not weather:
        st.error('Failed to retrieve weather data.')
    else:
        temp = weather['temperature']
        rh = weather['relativehumidity']
        wind = weather['windspeed']
        solar = weather.get('solar_radiation', 0) or 0
        hi = calc_heat_index(temp, rh)
        wbgt = calc_wbgt(temp, rh, wind, solar)
        col1, col2 = st.columns(2)
        with col1:
            st.metric('Temperature (°C)', f"{temp:.1f}")
            st.metric('Relative Humidity (%)', f"{rh}")
        with col2:
            st.metric('Wind Speed (km/h)', f"{wind}")
            st.metric('Solar Radiation (W/m²)', f"{solar}")
        st.subheader('Heat Stress Metrics')
        heat_index_gauge(hi)
        wbgt_gauge(wbgt)
        # Risk badge
        hi_risk = classify_risk(hi)
        wbgt_risk = classify_risk(wbgt)
        st.markdown(f"**Heat Index Risk:** <span style='color:{hi_risk['colour']}'>{hi_risk['tier']}</span>")
        st.markdown(f"**WBGT Risk:** <span style='color:{wbgt_risk['colour']}'>{wbgt_risk['tier']}</span>")

# Forecast tab (simple line chart)
with tabs[1]:
    st.header('3‑Day Forecast')
    df = get_forecast(lat, lon, days=3)
    if not df.empty:
        st.line_chart(df.set_index('time')[['temperature', 'relativehumidity']])
    else:
        st.info('Forecast data unavailable.')

# Advisory tab – age group selection
with tabs[2]:
    st.header('Personalized Advisory')
    age_group = st.selectbox('Select Age Group', ['child', 'adult', 'elderly'], index=1)
    if 'live_badge' not in st.session_state:
        # Ensure we have latest risk tier from live monitor
        st.session_state['live_badge'] = ''
    # Use the most recent HI risk tier from live monitor if available
    risk_tier = hi_risk['tier'] if 'hi_risk' in locals() else 'Normal'
    advisory = get_advisory(age_group, risk_tier)
    st.success(advisory)

# Map tab – placeholder (Folium integration can be added later)
with tabs[3]:
    st.header('Geospatial View')
    st.info('Map visualization will be integrated here using Folium.')

# Officer Portal – limited view for now
if role == 'officer':
    with tabs[4]:
        st.header('Officer Dashboard')
        st.markdown('**Current Alerts**')
        st.info('Alert management features (create, edit, dismiss) can be added in future iterations.')
else:
    # Hide officer tab for citizens by replacing content
    with tabs[4]:
        st.write('')
