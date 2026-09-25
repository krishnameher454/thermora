import streamlit as st

def render_header():
    """Render the top header with logo, title and live badge.
    Also inject custom CSS for the Option A dark theme.
    """
    # Custom CSS for dark theme and alert colors
    custom_css = """
    <style>
    body {
        background-color: #0b1424;
        color: #e5e7eb;
    }
    .sidebar .sidebar-content {
        background-color: #0b1424;
        color: #e5e7eb;
    }
    .st-emotion-cache-1t2wpf2 {  /* Main container */
        background-color: #0b1424;
    }
    .alert-danger {color: #ef4444; font-weight: bold;}
    .alert-amber {color: #f59e0b; font-weight: bold;}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    # Simple SVG logo (placeholder)
    logo_svg = """
    <svg width=\"40\" height=\"40\" viewBox=\"0 0 100 100\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\">
      <circle cx=\"50\" cy=\"50\" r=\"45\" stroke=\"#ef4444\" stroke-width=\"5\" />
      <text x=\"50%\" y=\"55%" dominant-baseline=\"middle\" text-anchor=\"middle\" fill=\"#ef4444\" font-size=\"40\" font-family=\"Arial, Helvetica, sans-serif\">☀</text>
    </svg>
    """
    st.image(logo_svg, format='svg', width=50)
    st.title("HeatAlert – SIH 2026 (MoES)")
    st.subheader("Extreme Heatwave Early Warning System")
    st.caption("Real‑time data, risk classification, actionable guidance.")

    # Live data badge (placeholder – updated in main app)
    if 'live_badge' in st.session_state:
        st.markdown(st.session_state['live_badge'], unsafe_allow_html=True)
