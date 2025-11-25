# Email Productivity Agent — React Frontend (Prototype)

This folder contains a Vite + React prototype frontend scaffold for the "AI Email Agent" application. It recreates the Streamlit UI as a polished SPA using Chakra UI + Tailwind and a small mocked API layer.

Tech: Vite, React, Chakra UI, Tailwind CSS, Lucide Icons, Axios (mock), React Query.

Run locally (from /frontend):

1. Install dependencies

```powershell
cd frontend; npm install
```

2. Start dev server

```powershell
npm run dev
```

Files added
- `src/App.jsx` — routing and layout (left sidebar + main content)
- `src/components/Sidebar.jsx` — controls, ingestion actions and navigation
- `src/components/Inbox.jsx` — Smart Inbox with expandable cards, draft editing
- `src/components/AgentBrain.jsx` — interface to edit system prompts
- `src/components/ChatInterface.jsx` — chat UI for RAG-style replies
- `src/services/api.js` — mocked backend using setTimeout

Notes
- The mock `api.js` keeps in-memory data and is safe for testing features locally. Replace with real API endpoints (Axios or fetch) when backend is ready.
- Default theme is dark and tuned towards high-contrast slate/gray tones to match the Streamlit prototype.
