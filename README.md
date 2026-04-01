# 🛡️ SafeRouteAI

> **AI-powered women's safety map for Mumbai & Delhi**  
> Community-driven incident reporting + real-time AI safety assessments

![SafeRouteAI](https://img.shields.io/badge/Status-Live-brightgreen) ![Python](https://img.shields.io/badge/Python-3.12-blue) ![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey) ![AI](https://img.shields.io/badge/AI-Groq%20LLaMA%203.3-orange) ![Data](https://img.shields.io/badge/Incidents-162%2B-red)

---

## 🌍 What is SafeRouteAI?

SafeRouteAI is a community-powered safety platform that helps women make informed decisions about where they travel in Mumbai and Delhi. Anyone can report an unsafe incident — harassment, poor lighting, stalking, theft — and anyone can check how safe an area is before they go.

The more people report, the smarter and more accurate it gets.

---

## 🔥 How it works

```
User clicks any area on the map
          ↓
App checks: how many incidents reported nearby?
          ↓
Sends data to Groq AI (LLaMA 3.3 70B)
          ↓
AI analyses patterns and returns:
Safety Score (0–100) + Plain English Summary + Safety Tip
          ↓
Displayed instantly on screen
```

---

## ✨ Features

- 🗺️ **Interactive Safety Map** — Leaflet.js map of Mumbai & Delhi with live incident pins
- 🔴 **Community Reporting** — Anyone can report harassment, poor lighting, stalking, theft, unsafe areas
- 🤖 **AI Safety Assessment** — Click any area to get an instant AI-generated safety score and summary
- 📊 **Real Data Pre-loaded** — 162+ incidents seeded from real sources including Mumbai Police reports, NCRB 2023 data, and NARI 2025 survey
- 🌆 **Two Cities** — Switch between Mumbai and Delhi instantly
- 📱 **Mobile Friendly** — Works on all screen sizes
- ⚡ **Real-time Feed** — See latest community reports in the sidebar
- 🆓 **100% Free** — No paywalls, no sign-ups, no ads

---

## 🧠 Data Sources

The pre-loaded incident data is sourced from:

- **Mumbai Police** — 437 identified unsafe spots for women (official report)
- **NCRB 2023** — National Crime Records Bureau crimes against women data
- **NARI 2025** — National Commission for Women safety survey (12,770 women across 31 cities)
- **OpenCity.in** — Mumbai crime data 2023
- Known hotspots: Aarey Colony, Paharganj, Kashmere Gate, Chowpatty, old mill compounds, Connaught Place and more

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python + Flask |
| AI | Groq API (LLaMA 3.3 70B — free tier) |
| Database | SQLite |
| Map | Leaflet.js + OpenStreetMap |
| Frontend | Vanilla JS + HTML + CSS |
| Deployment | Render |

---

## 📁 Project Structure

```
SafeRouteAI/
├── main.py              # Flask backend — all API routes
├── seed_data.py         # 162+ real incidents loader
├── requirements.txt     # Python dependencies
├── .env                 # API keys (never committed)
├── .gitignore
└── templates/
    └── index.html       # Entire frontend (HTML + CSS + JS)
```

---

## 🚀 Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/SafeRouteAI.git
cd SafeRouteAI
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your API key**

Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get a free key at [console.groq.com](https://console.groq.com)

**4. Seed the database**
```bash
python seed_data.py
```

**5. Run the app**
```bash
python main.py
```

Open `http://localhost:5000`

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/incidents` | Fetch all incidents (filter by `?city=Mumbai`) |
| POST | `/api/incidents` | Submit a new incident report |
| GET | `/api/assess` | Get AI safety assessment for coordinates |
| POST | `/api/incidents/<id>/upvote` | Upvote a community report |
| GET | `/api/stats` | City-wide safety statistics |

---

## 📊 Current Data

| City | Incidents |
|------|-----------|
| Mumbai | 75 |
| Delhi | 87 |
| **Total** | **162** |

*Data grows with every community report*

---

## 🗺️ Coverage Areas

**Mumbai** — Aarey Colony, Lower Parel Mills, Chowpatty, CST, Colaba, Dadar, Andheri, Kurla, Dharavi, Sion, Bandra, Malad, Borivali, Govandi, Mankhurd, Mira Road, Navi Mumbai and more

**Delhi** — Paharganj, Kashmere Gate, Old Delhi, Connaught Place, Dwarka, Rohini, Laxmi Nagar, Saket, Sangam Vihar, Mustafabad, Okhla, Trilokpuri, Najafgarh, Anand Vihar, Shahdara and more

---

## 🤝 Contributing

This is an open-source community safety project. Contributions welcome:

- Add more incident data for new cities
- Improve the AI prompt for better assessments
- Add new features (route planning, SOS button, etc.)
- Report bugs or suggest improvements via Issues

---

## 📈 Roadmap

- [ ] Add Bengaluru and Chennai
- [ ] SOS emergency button
- [ ] Safe route suggestions between two points
- [ ] WhatsApp integration for reporting
- [ ] Heatmap overlay
- [ ] Offline mode
- [ ] Mobile app (React Native)

---

## ⚠️ Disclaimer

SafeRouteAI is a community-driven platform. Incident data is user-reported and AI assessments are based on available community reports. Always trust your instincts. In an emergency call **112** (India emergency number).

---

## 👨‍💻 Built by

Built as an open-source social impact project to help make Indian cities safer for women.

*If this helped you or someone you know, please ⭐ the repo and share it.*

---

**📍 Live at:** (https://saferouteai-zbf0.onrender.com)
