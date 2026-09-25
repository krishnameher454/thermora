# Thermora – HeatAlert Streamlit Application

## Overview
A zero‑cost Python Streamlit web app that:
- Retrieves real‑time weather data from **Open‑Meteo** (free API).
- Calculates **Heat Index** and **WBGT**.
- Classifies heat‑stress risk using the **Emergency Disaster Command Center** dark theme (Option A).
- Provides personalized health advisories for children, adults, and the elderly.
- Supports two roles: **Citizen** (default) and **Disaster Officer** (extra dashboard).

The project lives in the `heatwave_app/` folder and is ready to run locally and be shared via a public URL.

---
## Quick Start (Local)
```powershell
# Navigate to the project folder
cd C:\Users\ASUS\Desktop\Thermora\heatwave_app

# (Optional) create a virtual environment
python -m venv venv
.\venv\Scripts\activate   # PowerShell
# On CMD: venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```
The app will be available at `http://localhost:8501`. Open that URL in a browser, log in with any username/password, and explore the UI.

---
## Sharing with Your Team
You can share the app **without requiring each teammate to run the code locally** by deploying it to a free hosting service. Two simple options are provided.

### 1️⃣ Deploy to Streamlit Cloud (recommended)
1. **Create a free GitHub repository** and push the `heatwave_app/` folder.
   ```powershell
   cd C:\Users\ASUS\Desktop\Thermora\heatwave_app
   git init
   git add .
   git commit -m "Initial commit – Thermora Streamlit app"
   # Replace <YOUR-USERNAME>/<YOUR-REPO> with your own names
   git remote add origin https://github.com/<YOUR-USERNAME>/<YOUR-REPO>.git
   git branch -M main
   git push -u origin main
   ```
2. Sign in to **[Streamlit Cloud](https://share.streamlit.io/)** with your GitHub account.
3. Click **"New app"**, select the repository you just pushed, and set the main file to `app.py`.
4. Click **"Deploy"**. After a few seconds the service provides a public URL such as `https://your‑app‑name.streamlit.app/`.
5. **Share that URL** with your teammates – they can open it in any browser, no installation needed.

### 2️⃣ Expose a Local Run via Cloudflare Tunnel (no GitHub needed)
If you prefer to keep the app running on your machine and expose it temporarily:
1. Install Cloudflare Tunnel (free) – see the official guide: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation
2. From the project folder, start the tunnel:
   ```powershell
   cloudflared tunnel --url http://localhost:8501
   ```
3. Cloudflare will output a **public URL** (e.g., `https://random-subdomain.trycloudflare.com`). Share that link with your team.
4. When you stop the tunnel, the link becomes inactive.

> **Note:** The Cloudflare method works only while your computer is on and the Streamlit process is running.

---
## Folder Structure
```
heatwave_app/
├─ app.py                 # Main Streamlit entry point
├─ auth.py                # Simple login & role handling
├─ weather_service.py     # Open‑Meteo wrapper + fallback data
├─ metrics_engine.py      # HI, WBGT, risk tiers, advisories
├─ components/
│   ├─ header.py         # Logo, title, custom CSS (Option A dark theme)
│   └─ gauges.py         # Plotly gauge visualisations
├─ requirements.txt       # Python dependencies
├─ README.md              # *This file*
└─ tests/
    └─ test_metrics.py   # Unit tests for metric calculations
```

---
## Running Tests (optional)
```powershell
pip install pytest   # already in requirements.txt
pytest tests/test_metrics.py
```
All tests should pass, confirming the correctness of the Heat Index and WBGT formulas.

---
## Next Enhancements (optional)
- Add a full **Folium map** with heat‑stress markers.
- Implement an **Officer alert management** CRUD interface.
- Store user sessions persistently (OAuth, etc.).
- Provide automated alerts via email/SMS.

---
Feel free to reach out if you need help creating the GitHub repo, configuring Streamlit Cloud, or setting up the Cloudflare tunnel. Happy hacking! 🎯
