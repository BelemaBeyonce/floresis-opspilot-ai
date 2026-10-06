# Floresis OpsPilot AI

**Enterprise operational intelligence for grounded question-answering over organizational knowledge.**

Floresis OpsPilot AI is a backend-focused enterprise AI project designed to help organizations retrieve useful information from internal operational documents such as policies, reports, standard operating procedures (SOPs), project updates, and governance documents.

Instead of manually searching through multiple documents, users can ask operational questions and receive answers grounded in available organizational evidence, with source citations and persisted query runs for auditability.

> **Project Status:** v0.1 — Functional MVP

---

## The Problem

Organizations generate large amounts of internal knowledge across:

- Policies
- Standard Operating Procedures (SOPs)
- Project reports
- Operational updates
- Governance documents
- Incident reports
- Internal guidelines

Finding the right information quickly can become difficult as the volume of documentation grows.

Floresis OpsPilot AI explores how an internal knowledge system can make this information easier to retrieve while maintaining **evidence, traceability, and auditability**.

---

## How It Works

The current MVP follows this workflow:

```text
Organizational Documents
        ↓
Document Ingestion
        ↓
Database Storage
        ↓
Query
        ↓
Evidence Retrieval
        ↓
Grounded Response
        ↓
Source Citations
        ↓
Persisted Run / Audit Record
```

For example, a user can ask:

```text
Which project is behind schedule and why?
```

OpsPilot searches the available organizational knowledge, identifies relevant evidence, and returns a grounded response with references to the source documents.

---

## Current MVP Features

The current version implements:

- FastAPI REST backend
- Document ingestion
- Organizational knowledge storage
- SQLite persistence
- Keyword-based evidence retrieval
- Grounded question answering
- Source citations
- Persisted query runs
- Audit-friendly response history
- Interactive web interface
- Automatic FastAPI API documentation
- Automated API tests
- Docker configuration

The current retrieval implementation is intentionally lightweight and deterministic. It does **not** yet use an external LLM or vector database.

---

## Architecture

```text
                 ┌──────────────────────┐
                 │      Web Client      │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │    FastAPI REST API  │
                 └──────────┬───────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
       Document Management       Query / Retrieval
                │                       │
                └───────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │      SQLAlchemy      │
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │        SQLite        │
                 └──────────────────────┘
```

Additional architecture information is available in `ARCHITECTURE.md`.

---

## Tech Stack

**Backend**

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

**Data**

- SQLite

**Testing**

- Pytest
- FastAPI TestClient

**Infrastructure**

- Docker
- Docker Compose

**Frontend**

- HTML
- CSS
- JavaScript

---

## Project Structure

```text
floresis-opspilot-ai/
│
├── app/
│   ├── main.py
│   └── static/
│
├── tests/
│   └── test_api.py
│
├── ARCHITECTURE.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Running the Project Locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd floresis-opspilot-ai
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
source .venv/Scripts/activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the API

```bash
uvicorn app.main:app --reload
```

Open the application at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Running Tests

Run:

```bash
python -m pytest
```

The current MVP includes automated tests covering API health and the core grounded retrieval workflow.

---

## Example Workflow

1. Start the application.
2. Open the web interface.
3. Click **Load demo workspace**.
4. Ask:

```text
Which project is behind schedule and why?
```

5. OpsPilot retrieves relevant internal evidence.
6. The response includes the supporting source information.
7. The query and response are persisted for auditability.

---

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health check |
| POST | `/api/documents` | Add an organizational document |
| GET | `/api/documents` | Retrieve available documents |
| POST | `/api/ask` | Ask a grounded operational question |
| POST | `/api/seed` | Load demonstration organizational data |
| GET | `/docs` | Interactive API documentation |

---

## Roadmap

Floresis OpsPilot AI is being developed incrementally.

Planned improvements include:

- PostgreSQL
- pgvector
- Document chunking
- Embedding generation
- Semantic vector search
- LLM-powered Retrieval-Augmented Generation (RAG)
- File upload and document parsing
- User authentication
- Role-Based Access Control (RBAC)
- Multi-tenant organizational workspaces
- Redis
- Background task processing
- Asynchronous document ingestion
- Evaluation datasets
- RAG quality evaluation
- Structured audit logging
- Observability
- CI/CD
- Cloud deployment

These capabilities are part of the planned architecture and are **not represented as implemented features in the current MVP**.

---

## Target Architecture

The longer-term architecture will evolve toward:

```text
Documents
    ↓
Document Processing
    ↓
Chunking
    ↓
Embedding Model
    ↓
PostgreSQL + pgvector
    ↓
Semantic Retrieval
    ↓
RAG Pipeline
    ↓
LLM
    ↓
Grounded Response + Citations
    ↓
Audit / Evaluation / Observability
```

The goal is to evolve Floresis from a deterministic retrieval MVP into a production-oriented enterprise AI knowledge platform.

---

## Why This Project Exists

Floresis OpsPilot AI is being built as a practical exploration of the intersection between:

**Backend Engineering + Applied AI + Enterprise Knowledge Systems + AI Governance**

The project focuses not only on generating AI responses, but also on the engineering concerns surrounding enterprise AI systems:

- Where did the answer come from?
- What evidence supports it?
- Can the interaction be audited?
- How should organizational knowledge be isolated?
- How should access be controlled?
- How can retrieval quality be evaluated?
- How can AI workflows be deployed reliably?

---

## Author

**Tamuno-Belema Adim**

Backend Developer | Applied AI / Machine Learning Engineer

---

## Current Status

**v0.1 — Functional MVP**

The initial backend, persistence layer, retrieval workflow, API, web interface, tests, and Docker configuration are operational.

Development is ongoing toward a production-oriented RAG architecture.