# 🧠 RelAI — Relationship Intelligence Pipeline

An AI-powered system that analyzes communication patterns and automates relationship maintenance using behavioral scoring, anomaly detection, and Claude AI.

---

the deployed link is https://relationship-ai.streamlit.app/

## 🏗️ Architecture

```
Raw Chat Data
     │
     ▼
[1] Ingestion & Parsing
     │  synthetic_generator.py → chats.json
     │
     ▼
[2] Feature Extraction          pipeline/features.py
     │  · Recency, Frequency, Reciprocity
     │  · Sentiment, Reply Latency, Plan Detection
     │  · Silence Gap Analysis
     │
     ▼
[3] Scoring Engine              pipeline/scoring.py
     │  · Weighted Health Score (0–100)
     │  · Grade: A / B / C / D
     │  · Sub-scores per dimension
     │
     ▼
[4] Anomaly Detection           pipeline/scoring.py
     │  · Sudden silence, One-sided conversations
     │  · Frequency decay, Unresolved plans, Dormancy
     │
     ▼
[5] AI Decision Engine          pipeline/decision.py
     │  · Claude analyzes each at-risk contact
     │  · Determines action type + urgency
     │  · Drafts personalized outreach message
     │
     ▼
[6] Streamlit Dashboard         dashboard/app.py
     · Health score overview
     · Contact profiles with metrics
     · AI action center
     · Conversation timeline viewer
```

---

## 📊 Scoring Weights

| Dimension    | Weight | What it measures |
|-------------|--------|-----------------|
| Recency     | 28%    | Days since last contact |
| Frequency   | 22%    | Message volume + trend |
| Reciprocity | 20%    | Who initiates, balance |
| Sentiment   | 15%    | Emotional tone |
| Engagement  | 15%    | Depth, plans, response time |

---

## 🤖 AI Actions Triggered

| Action | When |
|--------|------|
| `send_nudge` | Score dropping, silent too long |
| `follow_up_plan` | Unresolved plan detected |
| `reconnect` | Dormant relationship |
| `check_in` | One-sided conversation |
| `maintain` | Healthy — positive reinforcement |

---

## 📁 Project Structure

```
relationship-ai/
├── data/
│   ├── synthetic_generator.py   # Creates fake but realistic chat data
│   └── chats.json               # Generated dataset
├── pipeline/
│   ├── features.py              # Behavioral feature extraction
│   ├── scoring.py               # Health score + anomaly detection
│   └── decision.py              # Claude AI decision engine
├── dashboard/
│   └── app.py                   # Streamlit UI
├── main.py                      # Full pipeline runner
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

- **Python 3.11+**
- **Anthropic Claude API** — AI reasoning & message drafting
- **Pandas + NumPy** — behavioral feature computation
- **Streamlit** — interactive dashboard
- **Plotly** — charts and visualizations
- **Faker** — synthetic data generation
# relationship-ai
