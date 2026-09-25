import plotly.graph_objects as go
import streamlit as st
from metrics_engine import classify_risk

def _gauge(value: float, label: str, metric: str = "HI"):
    tier = classify_risk(value, metric)
    steps = [
        {"range": [0,  26], "color": "#10b98133"},
        {"range": [27, 32], "color": "#fcd34d33"},
        {"range": [33, 38], "color": "#f59e0b33"},
        {"range": [39, 45], "color": "#f9731633"},
        {"range": [46, 60], "color": "#ef444433"},
    ]
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        number={"suffix": " °C", "font": {"color": "#e5e7eb", "size": 28}},
        gauge={
            "axis": {"range": [0, 55], "tickcolor": "#94a3b8",
                     "tickfont": {"color": "#94a3b8"}},
            "bar":  {"color": tier["colour"], "thickness": 0.25},
            "bgcolor": "#1e293b",
            "borderwidth": 0,
            "steps": steps,
            "threshold": {
                "line": {"color": tier["colour"], "width": 4},
                "thickness": 0.85,
                "value": value,
            },
        },
        title={"text": f"{label}<br><span style='color:{tier['colour']};font-size:14px'>"
                       f"● {tier['tier']}</span>",
               "font": {"color": "#e5e7eb", "size": 16}},
    ))
    fig.update_layout(
        paper_bgcolor="#0b1424",
        font_color="#e5e7eb",
        height=280,
        margin={"t": 80, "b": 0, "l": 20, "r": 20},
    )
    st.plotly_chart(fig, use_container_width=True)

def heat_index_gauge(hi: float):
    _gauge(hi, "Heat Index (°C)", "HI")

def wbgt_gauge(wbgt: float):
    _gauge(wbgt, "WBGT (°C)", "HI")

def utci_gauge(utci: float):
    from metrics_engine import UTCI_TIERS
    tier = classify_risk(utci, "UTCI")
    steps = [
        {"range": [-20, 9],  "color": "#10b98133"},
        {"range": [9,  26],  "color": "#fcd34d33"},
        {"range": [26, 32],  "color": "#f59e0b33"},
        {"range": [32, 38],  "color": "#f9731633"},
        {"range": [38, 60],  "color": "#ef444433"},
    ]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=utci,
        number={"suffix": " °C", "font": {"color": "#e5e7eb", "size": 28}},
        gauge={
            "axis": {"range": [-20, 60], "tickcolor": "#94a3b8",
                     "tickfont": {"color": "#94a3b8"}},
            "bar":  {"color": tier["colour"], "thickness": 0.25},
            "bgcolor": "#1e293b",
            "borderwidth": 0,
            "steps": steps,
        },
        title={"text": f"UTCI (°C)<br><span style='color:{tier['colour']};font-size:14px'>"
                       f"● {tier['tier']}</span>",
               "font": {"color": "#e5e7eb", "size": 16}},
    ))
    fig.update_layout(
        paper_bgcolor="#0b1424",
        font_color="#e5e7eb",
        height=280,
        margin={"t": 80, "b": 0, "l": 20, "r": 20},
    )
    st.plotly_chart(fig, use_container_width=True)
