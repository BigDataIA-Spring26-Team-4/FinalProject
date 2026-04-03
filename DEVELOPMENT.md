# Maritime AI Sentinel — Development Guide

> Setup, running, and development instructions for the project.
> For the project proposal, see [README.md](README.md).

## Quick Start

### Prerequisites
- Python 3.12.x ([download](https://www.python.org/downloads/release/python-31210/))
- [Poetry](https://python-poetry.org/docs/#installation) — dependency management
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — for Redis, ChromaDB, Airflow
- Git

### 1. Clone & Install

```bash
git clone https://github.com/BigDataIA-Spring26-Team-4/FinalProject.git
cd FinalProject
poetry install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys (see API Keys section below)
```

### 3. Run POCs (no Docker needed)

```bash
# POC 1: Live AIS vessel tracking (needs AISSTREAM_API_KEY)
poetry run python poc/poc1_ais_streaming.py

# POC 2: GDELT geopolitical EDA (no API key needed)
poetry run python poc/poc2_gdelt_eda.py

# POC 3: OFAC sanctions + embeddings (needs OPENAI_API_KEY)
poetry run python poc/poc3_sanctions_embedding.py

# POC 4: LangGraph agent demo (needs OPENAI_API_KEY)
poetry run python poc/poc4_langgraph_agent.py
```

### 4. Run Tests

```bash
poetry run pytest -v
```

### 5. Start Full Stack (Docker)

```bash
docker compose up --build
```

Services will be available at:
| Service | URL | Purpose |
|---|---|---|
| FastAPI | http://localhost:8000 | REST API + OpenAPI docs at `/docs` |
| Streamlit | http://localhost:8501 | Dashboard |
| Airflow | http://localhost:8080 | DAG UI (admin/admin) |
| ChromaDB | http://localhost:8200 | Vector store |
| Redis | localhost:6379 | Cache |

---

## API Keys

| Key | Where to Get | Required For |
|---|---|---|
| `AISSTREAM_API_KEY` | https://aisstream.io (free registration) | POC 1, AIS streaming pipeline |
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys | POC 3, POC 4, embeddings, GPT-4o-mini agents |
| `ANTHROPIC_API_KEY` | https://console.anthropic.com/ | Claude Sonnet supervisor/news analyst agents |
| `SNOWFLAKE_ACCOUNT` | Your Snowflake account | Data warehouse |
| `ACLED_API_KEY` | https://developer.acleddata.com/ (free academic) | Conflict data pipeline |
| `WEATHER_API_KEY` | https://developer.weather.com/ (freemium) | Weather alerts pipeline |
| `LANGCHAIN_API_KEY` | https://smith.langchain.com/ (free tier) | LangSmith tracing (optional) |

---

## Project Structure

```
FinalProject/
├── README.md                    # Project proposal
├── DEVELOPMENT.md               # This file — setup & dev guide
├── pyproject.toml               # Poetry dependencies
├── poetry.lock                  # Locked dependency versions
├── docker-compose.yml           # 7-service Docker orchestration
├── .env.example                 # Environment variable template
│
├── docker/                      # All Dockerfiles
│   ├── Dockerfile.api           # FastAPI
│   ├── Dockerfile.dashboard     # Streamlit
│   ├── Dockerfile.airflow       # Airflow (Python 3.11, own deps)
│   └── Dockerfile.ingestion     # AIS WebSocket consumer
│
├── src/maritime_sentinel/       # Core Python package
│   ├── config.py                # Pydantic Settings (.env loader)
│   ├── pipelines/
│   │   ├── bronze/              # Raw data loaders (GDELT, ACLED, OFAC, weather, static)
│   │   ├── silver/              # Cleaning, deduplication, trajectory analysis
│   │   └── gold/                # Risk scores, transit analytics, vessel profiles
│   ├── embeddings/              # OpenAI embedding pipeline + ChromaDB client
│   ├── agents/                  # LangGraph agents (supervisor + 5 specialists)
│   │   └── schemas.py           # Pydantic output schemas (RiskScore, RouteAdvisory, etc.)
│   ├── mcp_server/              # MCP server with 7 maritime tools
│   │   └── tools/               # Individual tool implementations
│   ├── guardrails/              # Input moderation, citation grounding, hallucination detection
│   ├── cache/                   # Redis client (Gold cache, MCP cache, AIS position cache)
│   └── db/                      # Snowflake connection management
│
├── api/                         # FastAPI backend
│   ├── main.py                  # App factory
│   └── routes/                  # /risk, /vessels, /alerts, /chat
│
├── dashboard/                   # Streamlit frontend
│   ├── app.py                   # Entry point
│   ├── pages/                   # Globe, heatmap, vessel search, alerts, EDA, chat
│   └── components/              # HITL approval panel
│
├── airflow/dags/                # Airflow DAGs (GDELT, ACLED, OFAC, weather, static)
├── ingestion/                   # AIS WebSocket streaming consumer
├── data/seed/                   # Chokepoint reference data (application-defined)
├── tests/                       # Unit + integration tests
├── poc/                         # Proof of concept scripts (real data, runnable)
└── docs/                        # Codelabs and additional documentation
```

---

## Data Flow

```
External Sources → Airflow DAGs / AIS Consumer → Snowflake Bronze → Silver → Gold
                                                                  ↓
                                                         Embedding Pipeline → ChromaDB
                                                                  ↓
                                                Gold + ChromaDB → Redis Cache → MCP Tools → LangGraph Agents
                                                                                              ↓
                                                                                    FastAPI → Streamlit Dashboard
```

**Two data stores, two purposes:**
- **Snowflake** = structured data (vessel positions, event codes, risk scores) → queried via SQL
- **ChromaDB** = unstructured text (news articles, sanctions descriptions) → queried via semantic search (RAG)
- **Redis** = caching layer between both stores and the agents/API

---

## Development Workflow

### Adding a new dependency
```bash
poetry add package-name
# For dev-only:
poetry add --group dev package-name
```

### Running linter
```bash
poetry run ruff check src/ tests/ api/
```

### Running a single test
```bash
poetry run pytest tests/unit/test_schemas.py -v
```

### Docker commands
```bash
# Start all services
docker compose up --build

# Start specific service
docker compose up redis chromadb

# View logs
docker compose logs -f fastapi

# Stop everything
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

### Snowflake setup
```sql
-- Run once to create the warehouse and database
CREATE WAREHOUSE IF NOT EXISTS MARITIME_XS 
  WAREHOUSE_SIZE = 'XSMALL' 
  AUTO_SUSPEND = 60 
  AUTO_RESUME = TRUE;

CREATE DATABASE IF NOT EXISTS MARITIME_SENTINEL;
USE DATABASE MARITIME_SENTINEL;

-- Bronze schema (raw ingestion)
CREATE SCHEMA IF NOT EXISTS BRONZE;
-- Silver schema (cleaned)
CREATE SCHEMA IF NOT EXISTS SILVER;
-- Gold schema (aggregated)
CREATE SCHEMA IF NOT EXISTS GOLD;
```

---

## Team

| Member | Role | Focus Areas |
|---|---|---|
| Deep Prajapati | LLM Engineer + ETL Lead | Agents, MCP, embeddings, streaming pipeline, architecture |
| Tapan Patel | Cloud Architect + Data Engineer | Snowflake, Airflow, FastAPI, Docker, CI/CD |
| Seamus McAvoy | QA/Test + Frontend | Streamlit, guardrails, testing, documentation |
