# Refund Easy — AI Refund Agent

An autonomous AI customer support agent that processes refund requests end-to-end without human intervention. Built with LangGraph, GPT-4o, FastAPI, and Streamlit.

**Live Demo:** [refund-easy.streamlit.app](https://refund-easy.streamlit.app) | **API:** [refund-easy-api.onrender.com](https://refund-easy-api.onrender.com/docs)

---

## Demo

Enter a Customer ID (C001–C021), select an order, and chat with Alex — the AI refund specialist.

> Note: The backend runs on Render's free tier and may take 30–60 seconds to wake up on the first request.

**Test scenarios:**

| Customer | Order | Scenario |
|---|---|---|
| C001 | ORD1001 | Standard APPROVED |
| C003 | ORD1003 | DENIED — final sale |
| C005 | ORD1005 | DENIED — digital product |
| C004 | ORD1004 | ESCALATED — over $500 |
| C006 | ORD1006 | APPROVED — damaged item, fees waived |
| C018 | ORD1020 | ESCALATED — $649.99 standing desk |
| C007 | ORD1007 | DENIED — outside 30-day window |
| C016 | ORD1016 | Multi-order customer |
| C019 | ORD1021 | APPROVED — damaged, within 7 days |
| Any | Any | Try pleading, pressure, harassment, prompt injection |

---

## Architecture

```
User (Streamlit UI)
        │
        ▼
FastAPI /chat endpoint
        │
        ▼
LangGraph Agent Graph
   ┌────┴────┐
Agent Node  Tool Node (with retry)
   │             │
   │    ┌────────┼──────────────┐
   │    ▼        ▼              ▼
   │  check   get_order    validate_policy
   │  previous             escalate_to_human
   │  refund               get_policy
   │
   ▼
GPT-4o (OpenAI)
        │
        ▼
SQLite Database + LangSmith Tracing
```

---

## Features

- **Duplicate detection** — checks prior decisions before processing any new request
- **Policy enforcement** — 6-rule validation engine (final sale, digital, return window, damaged, escalation threshold)
- **Retry mechanism** — tool node retries failed calls up to 2 times with 0.5s backoff on transient failures
- **Conversation history** — multi-turn context passed across all requests, agent never repeats itself
- **Kill switch** — abusive/harassing sessions terminated automatically, account flagged
- **Escalation routing** — requests ≥ $500 auto-escalated with ticket ID generated
- **LangSmith observability** — full trace logging for every agent run
- **Live agent trace panel** — every reasoning step, tool I/O, token cost, and latency visible in UI
- **Refund logs table** — all decisions persisted to SQLite, viewable in UI
- **Session management** — chat resets automatically when switching customers
- **Privacy protection** — agent refuses to reveal other customer data, system prompt, or personal account details
- **Prompt injection defense** — handles jailbreak attempts, ignores instruction override attempts
- **Language guard** — responds in English only, gracefully handles non-English input

---

## Agent Resilience

The agent is designed to hold firm against:

| Scenario | Behavior |
|---|---|
| Customer pleads or begs | Acknowledges empathetically, holds policy |
| Customer pressures or threatens | Stays calm, firm, does not escalate tone |
| Harassment or profanity | Kill switch — session terminated, account flagged |
| Prompt injection ("ignore instructions") | Refuses clearly, stays in character |
| Fake damage claim | Checks order data, rejects unsupported claim |
| Fake purchase date claim | System date is source of truth |
| Cannot return item | Empathetic denial, no override |
| Claims non-delivery (status: delivered) | Routes to support ticket, not refund |
| Asks for other customer data | Refuses, privacy protection enforced |
| Asks to reveal system prompt | Refuses, stays in character |

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | GPT-4o (OpenAI) |
| Agent Framework | LangGraph, LangChain |
| API | FastAPI |
| Frontend | Streamlit |
| Database | SQLite |
| Observability | LangSmith |
| Hosting (API) | Render |
| Hosting (UI) | Streamlit Cloud |
| Language | Python 3.11+ |

---

## Project Structure

```
refund-agent/
├── backend/
│   ├── agent.py          # LangGraph graph, system prompt, GPT-4o integration
│   ├── tools.py          # 5 tools: lookup, validation, escalation, policy, duplicate check
│   ├── main.py           # FastAPI endpoints, request handling, ticket generation
│   └── database.py       # SQLite schema, read/write operations
├── streamlit/
│   └── app.py            # Streamlit UI, chat interface, session management
├── data/
│   ├── customers.json    # 21 test customers with varied order scenarios
│   └── refund_policy.txt # TechMart refund policy (agent's source of truth)
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/deepekaguru/refund-easy.git
cd refund-easy
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root:

```env
OPENAI_API_KEY=your_openai_api_key
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=refund-easy
```

### 5. Initialize the database

```bash
python -c "from backend.database import init_db; init_db()"
```

### 6. Start the backend

```bash
uvicorn backend.main:app --reload
```

### 7. Start the frontend (new terminal)

```bash
streamlit run streamlit/app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## Agent Decision Flow

1. Check for duplicate refund request
2. If duplicate → return prior decision, continue conversation naturally
3. If new → look up order details via customer ID and order ID
4. Validate against refund policy (6 rules in strict order)
5. If amount ≥ $500 → escalate, generate ticket, notify customer
6. Return APPROVED / DENIED / ESCALATED with natural language response
7. Log decision, trace, and ticket to SQLite

---

## Refund Policy Rules (in order)

1. Final sale items → always DENIED
2. Digital products → always DENIED
3. Damaged items reported within 7 days → APPROVED, fees waived, prepaid label
4. Damaged items reported after 7 days → DENIED
5. Outside 30-day return window → DENIED
6. Amount ≥ $500 → ESCALATED to senior management
7. Standard return → APPROVED, full refund

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat` | Send a message, receive agent response + trace |
| GET | `/customers` | List all customers and orders |
| GET | `/logs` | View all refund request logs |
| GET | `/tickets` | View all escalation tickets |
| GET | `/health` | Health check |
| DELETE | `/clear-logs` | Clear all refund logs and tickets |
| GET | `/download-db` | Download SQLite database file |

---

## Production Considerations

What I'd add before a production deployment:

- **Rate limiting** — prevent request spamming per customer session
- **Authentication** — JWT tokens or API key validation on all endpoints
- **Structured logging** — replace print-based DEBUG with Python `logging` module
- **Error alerting** — Sentry or PagerDuty for agent failure notifications
- **PostgreSQL** — replace SQLite with PostgreSQL on RDS for concurrent request handling
- **Cost monitoring** — OpenAI spend limits and token usage alerts
- **Response caching** — cache repeated identical requests to reduce API costs

---

## Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o |
| `LANGCHAIN_API_KEY` | LangSmith API key for tracing |
| `LANGCHAIN_TRACING_V2` | Enable LangSmith tracing (`true`/`false`) |
| `LANGCHAIN_PROJECT` | LangSmith project name |

