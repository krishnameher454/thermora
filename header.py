import streamlit as st

def render_header():
    """Render the top header with title and live badge.
    Also inject custom CSS for the Option A dark theme.
    """
    custom_css = """
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0b1424;
        color: #e5e7eb;
    }
    [data-testid="stSidebar"] {
        background-color: #111827;
        color: #e5e7eb;
    }
    [data-testid="stHeader"] {
        background-color: #0b1424;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e293b;
    }
    .stTabs [data-baseweb="tab"] {
        color: #e5e7eb;
    }
    .alert-danger { color: #ef4444; font-weight: bold; }
    .alert-amber  { color: #f59e0b; font-weight: bold; }
    div[data-testid="metric-container"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 10px;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: linear-gradient(90deg, #0b1424 0%, #1e293b 100%);
                padding: 20px; border-radius: 10px;
                border-left: 5px solid #ef4444; margin-bottom: 20px;">
        <h1 style="color:#ef4444; margin:0; font-size:2rem;">
            🌡️ THERMORA
        </h1>
        <p style="color:#f59e0b; margin:5px 0 0 0; font-size:1rem;">
            Extreme Heatwave Early Warning System &nbsp;|&nbsp;
            Ministry of Earth Sciences (MoES) &nbsp;|&nbsp; SIH 2026
        </p>
    </div>
    """, unsafe_allow_html=True)
