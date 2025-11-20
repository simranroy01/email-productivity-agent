import sqlite3
import json
import os
from datetime import datetime

# Defines paths relative to the root of the project
DB_FOLDER = 'data'
DB_NAME = 'email_agent.db'
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)
MOCK_DATA_PATH = os.path.join('assets', 'mock_inbox.json')

# --- DEFAULT PROMPTS (As per assignment requirements) ---
DEFAULT_PROMPTS = {
    "categorization": """
    Analyze the following email and categorize it into exactly one of these categories: 
    [Meeting, Newsletter, Spam, Task, Project Update].
    
    Rules:
    - 'Task': Must contain a direct request for action.
    - 'Meeting': Requests for time or calendar invites.
    - 'Spam': Promotional, lottery, or phishing attempts.
    - 'Project Update': Status reports or FYI emails with no immediate action.
    
    Return ONLY the category name.
    """,
    
    "action_items": """
    Extract action items and deadlines from the email text.
    Return a JSON object with a key 'tasks' containing a list of objects.
    Each object must have: 'description' (string) and 'deadline' (string or 'None').
    If no tasks are found, return { "tasks": [] }.
    """,
    
    "auto_reply": """
    Draft a professional, concise reply to this email based on the context.
    - If it's a meeting, ask for an agenda or confirm if the time works.
    - If it's a task, acknowledge receipt and estimate completion.
    - If it's spam, ignore it (return empty string).
    
    Sign off as 'Simran's AI Agent'.
    """
}

def get_connection():
    """Establishes a connection to the SQLite database."""
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    """Initializes the database tables and seeds default data."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Create Emails Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY,
        sender TEXT,
        subject TEXT,
        body TEXT,
        received_date TEXT,
        category TEXT,
        summary TEXT,
        action_items TEXT,  -- Stored as JSON string
        is_drafted BOOLEAN DEFAULT 0,
        reply_draft TEXT
    )
    ''')

    # 2. Create Prompts Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prompts (
        prompt_key TEXT PRIMARY KEY,
        prompt_text TEXT
    )
    ''')

    conn.commit()
    conn.close()
    
    # Run seeders
    seed_prompts()
    load_mock_data()

def seed_prompts():
    """Inserts default prompts if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    for key, text in DEFAULT_PROMPTS.items():
        # INSERT OR IGNORE ensures we don't overwrite user customizations on restart
        cursor.execute('INSERT OR IGNORE INTO prompts (prompt_key, prompt_text) VALUES (?, ?)', (key, text.strip()))
    
    conn.commit()
    conn.close()

def load_mock_data():
    """Loads mock emails from JSON if the email table is empty."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if emails already exist
    cursor.execute('SELECT count(*) FROM emails')
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("Inbox empty. Loading mock data...")
        if os.path.exists(MOCK_DATA_PATH):
            with open(MOCK_DATA_PATH, 'r') as f:
                emails = json.load(f)
                
            for email in emails:
                cursor.execute('''
                INSERT INTO emails (sender, subject, body, received_date)
                VALUES (?, ?, ?, ?)
                ''', (email['sender'], email['subject'], email['body'], email['received_date']))
            
            conn.commit()
            print(f"Successfully loaded {len(emails)} emails.")
        else:
            print(f"Warning: Mock data file not found at {MOCK_DATA_PATH}")
    
    conn.commit()
    conn.close()

# --- CRUD OPERATIONS ---

def fetch_emails():
    """Returns all emails ordered by date (newest first)."""
    conn = get_connection()
    emails = conn.execute('SELECT * FROM emails ORDER BY received_date DESC').fetchall()
    conn.close()
    return [dict(e) for e in emails]

def get_email_by_id(email_id):
    """Returns a single email dict."""
    conn = get_connection()
    email = conn.execute('SELECT * FROM emails WHERE id = ?', (email_id,)).fetchone()
    conn.close()
    return dict(email) if email else None

def update_email_analysis(email_id, category=None, action_items=None, summary=None):
    """Updates the processed fields (category, tasks) for an email."""
    conn = get_connection()
    query = "UPDATE emails SET "
    params = []
    updates = []
    
    if category:
        updates.append("category = ?")
        params.append(category)
    if action_items:
        # Ensure we store dict/list as JSON string
        if isinstance(action_items, (dict, list)):
            action_items = json.dumps(action_items)
        updates.append("action_items = ?")
        params.append(action_items)
    if summary:
        updates.append("summary = ?")
        params.append(summary)
        
    if not updates:
        conn.close()
        return

    updates.append("is_drafted = 0") # Reset draft status if re-analyzed
    
    query += ", ".join(updates) + " WHERE id = ?"
    params.append(email_id)
    
    conn.execute(query, params)
    conn.commit()
    conn.close()

def save_draft(email_id, draft_text):
    """Saves a generated reply draft."""
    conn = get_connection()
    conn.execute('UPDATE emails SET reply_draft = ?, is_drafted = 1 WHERE id = ?', (draft_text, email_id))
    conn.commit()
    conn.close()

def get_prompt(key):
    """Fetches a specific prompt template."""
    conn = get_connection()
    row = conn.execute('SELECT prompt_text FROM prompts WHERE prompt_key = ?', (key,)).fetchone()
    conn.close()
    return row['prompt_text'] if row else ""

def update_prompt_in_db(key, new_text):
    """Updates a prompt template."""
    conn = get_connection()
    conn.execute('UPDATE prompts SET prompt_text = ? WHERE prompt_key = ?', (new_text, key))
    conn.commit()
    conn.close()

# --- INITIALIZATION ON IMPORT ---
# This ensures DB exists as soon as this module is imported
init_db()
