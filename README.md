Intelligent Email Productivity Agent 📧

A full-stack AI-powered email assistant that doesn't just read emails but actively manages them. Built with a Prompt-Driven Architecture, allowing users to modify the agent's behavior (categorization rules, reply persona, extraction logic) purely by editing system prompts in the UI—no code changes required.

🚀 Key Features

🧠 Prompt-Driven Logic: The "Brain" of the agent lives in the database. Users can edit the "Auto-Reply Persona" or "Categorization Rules" in the dashboard, and the backend adapts instantly.

📥 Smart Ingestion Pipeline:

Auto-categorizes emails into Tasks, Meetings, Newsletters, and Spam.

Action Item Extraction: Automatically parses deadlines and deliverables from long email threads into structured JSON.

💬 RAG Chat Agent: Chat with your inbox ("What tasks did Sarah assign me?") using Retrieval Augmented Generation.

✍️ Human-in-the-Loop Drafting: The agent drafts replies but never sends them automatically. Users can review, edit, and save drafts safely.

⚡ Optimistic UI: The frontend simulates progress bars for immediate feedback while the backend processes heavy AI workloads.

🛠️ Tech Stack

Frontend (Client)

Framework: React (Vite)

Styling: Chakra UI + Tailwind CSS

State Management: React Query (TanStack Query)

Markdown Rendering: react-markdown

Backend (Server)

Framework: FastAPI (Python)

Database: SQLite (chosen for zero-config portability)

AI Engine: Google Gemini Pro / Groq (Llama 3)

Validation: Pydantic Models

⚙️ Installation & Setup

1. Clone the Repository

git clone [https://github.com/your-username/email-productivity-agent.git](https://github.com/your-username/email-productivity-agent.git)
cd email-productivity-agent


2. Backend Setup

Navigate to the root directory to set up the Python server.

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Environment
# Create a .env file in the root and add your API Key:
echo "GOOGLE_GEMINI_API_KEY=your_key_here" > .env


3. Frontend Setup

Navigate to the frontend directory.

cd frontend

# Install Node modules
npm install

# Configure Environment
# Create a .env file in frontend/ and add:
echo "VITE_API_URL=http://localhost:8000" > .env


▶️ Running Locally

You need to run the Backend and Frontend in two separate terminals.

Terminal 1 (Backend):

# Make sure you are in the root folder
python server.py
# Server runs at http://localhost:8000


Terminal 2 (Frontend):

cd frontend
npm run dev
# Client runs at http://localhost:5173


☁️ Deployment

Backend (Render)

Push code to GitHub.

Create a new Web Service on Render.

Build Command: pip install -r requirements.txt

Start Command: uvicorn server:app --host 0.0.0.0 --port 10000

Add Environment Variable: GOOGLE_GEMINI_API_KEY.

Frontend (Vercel)

Import the GitHub repo into Vercel.

Set Root Directory to frontend.

Add Environment Variable: VITE_API_URL = https://your-render-backend-url.onrender.com.