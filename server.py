from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import json
import time
from src import database, email_processor, prompt_manager, llm_service

# Try importing the AI generator, handle if missing
try:
    from src import ai_email_generator
except ImportError:
    ai_email_generator = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptUpdate(BaseModel):
    key: str
    text: str

class ChatRequest(BaseModel):
    message: str

class DraftUpdate(BaseModel):
    email_id: int
    draft_text: str

class StarUpdate(BaseModel):
    email_id: int
    is_starred: bool

@app.get("/emails")
def get_emails():
    """Fetch all emails. Database should have an 'is_starred' column."""
    # Ensure the 'is_starred' column exists (migration hack for dev)
    conn = database.get_connection()
    try:
        conn.execute("ALTER TABLE emails ADD COLUMN is_starred BOOLEAN DEFAULT 0")
    except:
        pass # Column likely exists
    conn.close()
    
    return database.fetch_emails()

@app.post("/ingest/load")
def load_inbox():
    database.clear_emails()
    gemini_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    loaded_source = "Local Mock Data"
    
    if gemini_key and ai_email_generator:
        try:
            inserted = ai_email_generator.generate_and_insert_ai_emails(num_emails=20)
            if inserted and inserted > 0:
                loaded_source = f"Gemini AI ({inserted} emails)"
            else:
                database.load_mock_data()
        except Exception as e:
            print(f"Gemini generation failed: {e}")
            database.load_mock_data()
    else:
        database.load_mock_data()
        
    return {"status": "success", "message": f"Inbox loaded from {loaded_source}"}

@app.post("/ingest/process")
def process_ai():
    # In a real app, we'd use a background task. 
    # For this demo, we run it synchronously so the frontend waits.
    email_processor.process_all_emails() 
    return {"status": "success", "message": "AI Processing Complete"}

@app.post("/system/reset")
def reset_system():
    """Wipe everything and reload default mock data"""
    # 1. Clear DB
    database.clear_emails()
    # 2. Reset Prompts
    prompt_manager.reset_defaults()
    # 3. Reload Mock Data immediately (The Fix)
    database.load_mock_data()
    return {"status": "success", "message": "System reset to initial mock state."}

@app.post("/emails/{email_id}/star")
def toggle_star(email_id: int, payload: StarUpdate):
    """Toggle star status"""
    conn = database.get_connection()
    conn.execute("UPDATE emails SET is_starred = ? WHERE id = ?", (payload.is_starred, email_id))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/emails/{email_id}/draft")
def generate_draft(email_id: int):
    draft = email_processor.generate_reply(email_id)
    return {"draft": draft}

@app.post("/emails/save-draft")
def save_draft_endpoint(payload: DraftUpdate):
    database.save_draft(payload.email_id, payload.draft_text)
    return {"status": "success"}

@app.get("/prompts")
def get_prompts():
    return prompt_manager.get_all_prompts()

@app.post("/prompts")
def update_prompt_endpoint(payload: PromptUpdate):
    success, msg = prompt_manager.update_prompt(payload.key, payload.text)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}

@app.post("/chat")
def chat_agent(payload: ChatRequest):
    emails = database.fetch_emails()
    recent_emails = emails[:15]
    
    context_str = ""
    for e in recent_emails:
        cat = e['category'] if e['category'] else "Uncategorized"
        context_str += f"From: {e['sender']}, Subj: {e['subject']}, Category: {cat}, Body: {e['body']}\n\n"

    full_query = f"""
    User Query: {payload.message}
    
    Context (Inbox Data):
    {context_str}
    
    INSTRUCTIONS:
    - You are a helpful Email Assistant.
    - Use Markdown formatting to make the response readable.
    - Use **Bold** for sender names or key terms.
    - Use bullet points (*) for lists.
    - Keep it concise but informative.
    """
    response = llm_service.get_llm_response(full_query)
    return {"response": response}

if __name__ == "__main__":
    print("🚀 Starting API Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)