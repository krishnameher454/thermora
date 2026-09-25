import plotly.graph_objects as go
import streamlit as st
from metrics_engine import classify_risk

def _gauge(value: float, label: str):
    tier_info = classify_risk(value)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': ' °C'},
        gauge={
            'axis': {'range': [None, max(50, value + 10)]},
            'bar': {'color': tier_info['colour']},
            'bgcolor': "#1e293b",
            'borderwidth': 2,
            'bordercolor': "#334155",
            'steps': [
                {'range': [0, 26], 'color': '#10b981'},
                {'range': [27, 32], 'color': '#fcd34d'},
                {'range': [33, 38], 'color': '#f59e0b'},
                {'range': [39, 45], 'color': '#f97316'},
                {'range': [46, 60], 'color': '#ef4444'},
            ],
        },
        title={'text': label, 'font': {'color': '#e5e7eb'}},
    ))
    fig.update_layout(paper_bgcolor="#0b1424", font_color="#e5e7eb")
    st.plotly_chart(fig, use_container_width=True)

def heat_index_gauge(hi: float):
    """Render a gauge for Heat Index value."""
    _gauge(hi, "Heat Index (°C)")

def wbgt_gauge(wbgt: float):
    """Render a gauge for WBGT value."""
    _gauge(wbgt, "WBGT (°C)")
