# ✈️ Yatra AI
> **"Plan smarter. Travel better."**  
> AI-powered travel planner built with **Gemma 4** (`gemma-4-31b-it`)

---

## 🌟 What is Yatra AI?

Yatra AI is an adaptive AI travel intelligence platform that generates personalized day-by-day trip itineraries, optimizes budgets, re-plans dynamically, and assists travelers through multi-turn conversations — all powered by **Gemma 4** as the core reasoning engine.

### Features
- 🗓️ **AI Trip Generator** — Personalized day-by-day itinerary from 8 inputs
- 💰 **Budget Optimizer** — Smart cost analysis and savings recommendations
- 🔄 **Smart Re-planner** — Re-plans instantly when your budget or plans change
- 💬 **Travel Chat Assistant** — Multi-turn conversation with trip context
- 🎒 **Packing Assistant** — Personalized checklist by destination & interests
- 🌐 **Hindi + English** — Full bilingual support

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| AI Model | Gemma 4 (`gemma-4-31b-it`) |
| AI SDK | `google-genai >= 2.25.0` |
| Backend | Python 3.11+ + FastAPI |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Config | pydantic-settings + python-dotenv |

---

## 🚀 Quick Start

### 1. Get a Gemma 4 API Key
Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey) and create an API key.

### 2. Clone the repo
```bash
git clone https://github.com/utpalupadhyay/Yatra-AI.git
cd Yatra-AI
```

### 3. Set up the backend
```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Configure your API key
```bash
# Copy the template
copy .env.example .env   # Windows
cp .env.example .env     # Mac/Linux

# Edit .env and add your key:
# GEMMA_API_KEY=your_key_here
```

### 5. Start the backend
```bash
python main.py
# Server runs at: http://localhost:8000
# API docs at:    http://localhost:8000/docs
```

### 6. Open the frontend
Open `frontend/index.html` in your browser.  
*(Use VS Code Live Server for best results)*

---

## 📁 Project Structure

```
Yatra-AI/
├── backend/
│   ├── main.py                        # FastAPI entry point
│   ├── requirements.txt
│   ├── .env.example                   # API key template (copy to .env)
│   └── app/
│       ├── core/config.py             # Settings & env vars
│       ├── models/trip.py             # Pydantic models
│       ├── services/gemma_service.py  # 🧠 Gemma 4 AI logic
│       └── api/routes/trip.py        # REST endpoints
└── frontend/
    ├── index.html
    └── assets/
        ├── css/styles.css
        └── js/
            ├── api.js
            ├── app.js
            └── markdown.js
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/trip/generate` | Generate itinerary |
| POST | `/api/v1/trip/replan` | Re-plan trip |
| POST | `/api/v1/chat` | Chat assistant |
| POST | `/api/v1/trip/packing` | Packing list |
| POST | `/api/v1/trip/optimize-budget` | Budget optimizer |

---

## 🔐 Security

- **Never commit `.env`** — it's in `.gitignore`
- The API key lives only on the server, never in frontend JS
- CORS is open (`*`) for hackathon demo — restrict in production

---

## 📄 License

MIT License — built for **Hackofest 2026**
