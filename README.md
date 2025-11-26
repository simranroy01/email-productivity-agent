# AI Email Productivity Agent 📧

A productivity assistant that analyses and helps manage your inbox: auto-categorization, action-extraction, draft-replies, plus a chat (RAG) interface to query your inbox.

This repository contains two developer-facing surfaces:

- A Streamlit demo app (root `app.py`) — this is the primary demo harness that shows the full prompt-driven email pipeline and the Agent Brain UI.
- A React + Vite prototype SPA (in `frontend/`) — a modern, dark-themed single-page application that mirrors the Streamlit flows and uses a mocked API for local testing.

Why this repo?

- Demonstrates a prompt-driven architecture: change classification, extraction, or reply persona via editable prompts in the UI.
- Shows a complete experimental stack: email ingestion → LLM processing → draft suggestion → human review.

----

## Quick start — Streamlit demo (Python)

This is the fastest way to run a fully-contained demo locally.

Prerequisites

- Python 3.10+
- Git

PowerShell commands

```powershell
# 1) Clone the repository (if you haven't already)
git clone https://github.com/simranroy01/email-productivity-agent.git
cd email-productivity-agent

# 2) Create & activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3) Install Python dependencies
pip install -r requirements.txt

# Optional: configure a cloud LLM key for generator (app will fall back to local mock data)
# Add a .env file containing e.g. GOOGLE_GEMINI_API_KEY=your_key_here

# 4) Run the Streamlit app
streamlit run app.py
```

Open http://localhost:8501 in your browser to view the demo.

----

## Frontend prototype — React + Vite (optional)

The `frontend/` directory is a standalone SPA built with React, Chakra UI and Tailwind. It ships with a mocked API in `frontend/src/services/api.js` so it runs independently of the Python demo server.

PowerShell commands

```powershell
cd frontend
npm install
npm run dev
```

The dev server starts at the Vite URL (commonly http://localhost:5173).

----

## Project structure (high-level)

```
.
├─ app.py                   # Streamlit UI entrypoint
├─ requirements.txt         # Python dependencies for the Streamlit app
├─ src/                     # Python business logic and LLM adapters
│  ├─ database.py
│  ├─ email_processor.py
│  ├─ llm_service.py
│  ├─ prompt_manager.py
│  └─ ai_email_generator.py
├─ frontend/                # Optional SPA prototype (React + Vite)
│  ├─ package.json
│  ├─ src/
│  │  ├─ components/        # Sidebar, Inbox, AgentBrain, ChatInterface
│  │  └─ services/api.js     # mocked APIs used by the SPA
│  └─ README.md
└─ tests/                   # Unit tests (pytest)
```

----

## Testing

Run Python tests from the project root (after creating/activating the venv):

```powershell
.venv\Scripts\activate
pytest -q
```

----

## Developer notes & suggestions

- The Streamlit demo checks for the `GOOGLE_GEMINI_API_KEY` environment variable and will attempt to generate AI emails if present; otherwise it uses local mock data.
- The SPA `frontend/` directory uses an in-memory mock API for quick UI/UX iteration — when ready you can replace or proxy calls to a small backend service (FastAPI/Express) to run end-to-end.
- Consider adding a small REST API and vector DB layer for a production-ready RAG experience.

----

## License

This project is licensed under the MIT License — see the `LICENSE` file in the repository root for full details.
