import folium
import streamlit as st
try:
    from streamlit_folium import st_folium
except ImportError:
    st_folium = None
from weather_service import INDIAN_CITIES, get_current_weather
from metrics_engine import calc_heat_index, classify_risk

TIER_COLOURS = {
    "Normal":           "green",
    "Caution":          "beige",
    "Extreme Caution":  "orange",
    "Danger":           "red",
    "Extreme Danger":   "darkred",
    "Unknown":          "gray",
}

def render_map(selected_lat: float, selected_lon: float, selected_name: str = "Selected"):
    """Render a Folium map of India with heat-stress markers for major cities."""
    if st_folium is None:
        st.warning("Map library not available. Install streamlit-folium.")
        return

    m = folium.Map(
        location=[22.5, 82.0],
        zoom_start=5,
        tiles="CartoDB dark_matter",
    )

    # Add selected city marker (live data)
    weather = get_current_weather(selected_lat, selected_lon)
    temp = weather.get("temperature", 35)
    rh   = weather.get("relativehumidity", 50) or 50
    hi   = calc_heat_index(temp, rh)
    risk = classify_risk(hi)
    colour = TIER_COLOURS.get(risk["tier"], "gray")

    folium.CircleMarker(
        location=[selected_lat, selected_lon],
        radius=18,
        color=colour,
        fill=True,
        fill_color=colour,
        fill_opacity=0.8,
        popup=folium.Popup(
            f"<b>{selected_name}</b><br>"
            f"Temp: {temp}°C | RH: {rh}%<br>"
            f"Heat Index: {hi}°C<br>"
            f"Risk: <b>{risk['tier']}</b>",
            max_width=200,
        ),
        tooltip=f"{selected_name} – {risk['tier']}",
    ).add_to(m)

    # Add pre-loaded Indian city markers (lightweight – no API call per city)
    for city in INDIAN_CITIES:
        if (abs(city["latitude"] - selected_lat) < 0.01 and
                abs(city["longitude"] - selected_lon) < 0.01):
            continue  # already marked above
        # Use a simple temperature estimate for background cities (no live API per city)
        folium.CircleMarker(
            location=[city["latitude"], city["longitude"]],
            radius=8,
            color="gray",
            fill=True,
            fill_color="gray",
            fill_opacity=0.5,
            tooltip=city["name"],
            popup=folium.Popup(
                f"<b>{city['name']}</b><br>Click 'Select' to load live data",
                max_width=200,
            ),
        ).add_to(m)

    # Legend
    legend_html = """
    <div style="position:fixed; bottom:30px; left:30px; z-index:1000;
                background:rgba(15,23,42,0.9); padding:12px; border-radius:8px;
                border:1px solid #334155; font-family:sans-serif; font-size:12px; color:#e5e7eb;">
        <b style="color:#ef4444;">🌡️ Heat Stress Legend</b><br>
        🟢 Normal (&lt;27°C)<br>
        🟡 Caution (27-32°C)<br>
        🟠 Extreme Caution (33-38°C)<br>
        🔴 Danger (39-45°C)<br>
        🆘 Extreme Danger (&gt;45°C)
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    result = st_folium(m, width="100%", height=500, returned_objects=[])
    return result
