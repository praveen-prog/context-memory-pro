# Context Memory Pro

> Location-aware reminder app that fires intelligent nudges when you arrive, dwell, or exit a location.

**Live demo:** https://uw4aoqlpr4.execute-api.us-east-1.amazonaws.com

Built for the **CockroachDB × AWS Hackathon 2026**

---

## The problem

You set a reminder to buy milk before heading to Walmart. You get there, fill your cart, and walk out — completely forgetting the milk. The reminder fired at the wrong time, in the wrong place.

**Context Memory Pro fixes this** — reminders fire when you're actually at the location where you need them.

---

## Features

- **Three smart triggers** — arrival, dwell (still inside?), and exit gate (leaving with unchecked items)
- **Add reminders from anywhere** — search any place by name via OpenStreetMap, no need to visit first
- **AI-powered nudges** — Groq LLM generates friendly context-aware messages
- **Semantic search** — CockroachDB vector search finds related tasks using HuggingFace embeddings
- **Voice input** — speak reminders hands-free
- **Full CRUD** — add, edit, delete, complete tasks
- **Nudge history** — full memory trail stored in CockroachDB
- **Stats** — live counts across all locations and nudges
- **PWA** — works on iPhone and Android without installation
- **Cost: ~$0** — fully serverless

---

## Architecture

```
iPhone PWA (Real GPS + Voice)
        ↓ HTTPS
Amazon API Gateway
        ↓
AWS Lambda (FastAPI · Python 3.11)
   ├── /location  → GPS · add · list
   ├── /tasks     → add · edit · delete · complete
   ├── /nudge     → generate · history
   ├── /search    → vector search · history
   └── /stats     → live counts
        ↓
CockroachDB Serverless     Groq API              HuggingFace
VECTOR(384) · pgvector     llama-3.1-8b-instant  all-MiniLM-L6-v2
7 tables · semantic search AI nudge generation   384-dim embeddings
        ↓
OpenStreetMap Nominatim (free place search)
```

---

## CockroachDB tools used

| Tool | How used |
|------|----------|
| MCP Server | Schema design + query development via Claude Code |
| Distributed Vector Indexing | VECTOR(384) column + pgvector cosine distance search |
| ccloud CLI | Cluster provisioning and management |
| Agent Skills Repo | Query patterns and best practices |

---

## AWS services used

| Service | How used |
|---------|----------|
| AWS Lambda | FastAPI backend — serverless, scales to zero |
| Amazon API Gateway | Public HTTPS endpoint with CORS |
| Amazon S3 | Lambda deployment packages |
| Amazon EventBridge | Dwell checker scheduled every 24 hours |
| AWS CloudFormation | Infrastructure as code — full stack recreatable |

---

## Tech stack

- **Frontend** — Vanilla HTML/CSS/JS PWA · Geolocation API · Web Speech API · Web Notifications API
- **Backend** — FastAPI · Python 3.11 · Mangum · psycopg2
- **Database** — CockroachDB Serverless · pgvector
- **AI** — Groq (llama-3.1-8b-instant) · HuggingFace (all-MiniLM-L6-v2)
- **Maps** — OpenStreetMap Nominatim

---

## Setup

### Prerequisites
- AWS account
- CockroachDB Serverless cluster
- Groq API key (free)
- HuggingFace API token (free)

### Local development

```bash
git clone https://github.com/praveen-prog/context-memory-pro.git
cd context-memory-pro

conda create -n context-memory-pro python=3.11 -y
conda activate context-memory-pro
pip install -r requirements.txt

cp .env.example .env
# Fill in your credentials

python setup_database.py
python seed_data.py
python setup_embeddings.py

uvicorn api.main:app --reload --port 8002
```

### Deploy to AWS

```bash
# From AWS CloudShell
aws s3 cp s3://your-bucket/pro/deploy_pro.sh ~/deploy_pro.sh
chmod +x ~/deploy_pro.sh

cat > ~/.env_pro << 'ENVEOF'
COCKROACHDB_HOST=your-cluster.cockroachlabs.cloud
COCKROACHDB_USER=your_user
COCKROACHDB_PASSWORD=your_password
COCKROACHDB_DATABASE=context_memory_pro
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.1-8b-instant
HUGGINGFACE_API_TOKEN=your_hf_token
GEOFENCE_RADIUS_METERS=150
DWELL_TRIGGER_MINUTES=10
ENVEOF

bash ~/deploy_pro.sh
```

---

## Database schema

```sql
users           -- user profiles
locations       -- geofenced locations with lat/lng/radius
tasks           -- reminders with VECTOR(384) embeddings
location_events -- GPS arrival/dwell/exit events
nudge_events    -- AI nudges fired (stored permanently)
task_completions-- completion history
caregiver_links -- future: caregiver alerts
```

---

## Cost

```
AWS Lambda     ~$0.000036/month
Amazon S3      ~$0.000001/month
CockroachDB    $0 (Serverless free tier)
Groq           $0 (free tier)
HuggingFace    $0 (free tier)
──────────────────────────────
Total          ~$0/month
```

---

## What's next

- Google Sign-in via AWS Cognito
- Firebase Cloud Messaging for background push
- Caregiver SMS alerts via Twilio
- Background GPS via service worker
- React Native mobile app
- Multi-language support (Tamil, Hindi)

---

## License

MIT