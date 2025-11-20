import json
import time
from src import database
from src import llm_service

def process_all_emails(progress_callback=None):
    """
    Iterates through all emails in the database and runs the LLM pipeline.
    
    Args:
        progress_callback (function, optional): A function to update UI progress bar.
                                              Signature: callback(current_step, total_steps, message)
    """
    emails = database.fetch_emails()
    total = len(emails)
    
    print(f"--- Starting Processing Pipeline for {total} emails ---")
    
    # Fetch the current "Brain" configuration (Prompts) from DB
    cat_prompt_template = database.get_prompt("categorization")
    action_prompt_template = database.get_prompt("action_items")

    for index, email in enumerate(emails):
        email_id = email['id']
        sender = email['sender']
        body = email['body']
        
        # UI Feedback: Update progress if a callback is provided
        if progress_callback:
            progress_callback(index / total, f"Processing email from {sender}...")

        # --- STEP 1: CATEGORIZATION ---
        try:
            # Dynamic Prompt Injection: We insert the email body into the user's prompt
            full_cat_prompt = f"{cat_prompt_template}\n\nEMAIL BODY:\n{body}"
            
            # Call LLM (Text Mode is fine for simple categorization)
            category = llm_service.get_llm_response(full_cat_prompt, json_mode=False)
            
            # Clean up response (sometimes LLMs add periods or spaces)
            category = category.replace("Category:", "").strip().strip(".")
            
        except Exception as e:
            print(f"Error categorizing email {email_id}: {e}")
            category = "Uncategorized"

        # --- STEP 2: ACTION ITEM EXTRACTION ---
        action_data = {"tasks": []} # Default empty state
        
        # Optimization: Only look for tasks if it's NOT Spam or Newsletter
        # This saves API credits and time, showing "Product Thinking"
        if category not in ["Spam", "Newsletter"]:
            try:
                full_action_prompt = f"{action_prompt_template}\n\nEMAIL BODY:\n{body}"
                
                # Call LLM (JSON Mode is CRITICAL here)
                action_data = llm_service.get_llm_response(full_action_prompt, json_mode=True)
                
                # Safety check: Ensure the response actually has the 'tasks' key
                if not isinstance(action_data, dict) or 'tasks' not in action_data:
                    action_data = {"tasks": []}
                    
            except Exception as e:
                print(f"Error extracting actions for {email_id}: {e}")

        # --- STEP 3: SAVE RESULTS TO DB ---
        database.update_email_analysis(
            email_id=email_id,
            category=category,
            action_items=action_data
        )
        
        print(f"Processed {email_id}: [{category}] - Found {len(action_data.get('tasks', []))} tasks")
        
        # Respect Rate Limits (Small sleep to be safe with free tiers)
        time.sleep(0.5)

    if progress_callback:
        progress_callback(1.0, "Processing Complete!")

def generate_reply(email_id):
    """
    Generates a reply draft for a specific email using the saved context.
    """
    email = database.get_email_by_id(email_id)
    if not email:
        return "Error: Email not found."
        
    # Fetch context and prompts
    reply_prompt_template = database.get_prompt("auto_reply")
    
    # Construct the prompt
    full_prompt = f"""
    {reply_prompt_template}
    
    ---
    INCOMING EMAIL CONTEXT:
    Sender: {email['sender']}
    Subject: {email['subject']}
    Category: {email['category']}
    Action Items: {email['action_items']}
    Original Body:
    {email['body']}
    """
    
    # Generate Draft
    draft = llm_service.get_llm_response(full_prompt, json_mode=False)
    
    # Save to DB so it persists
    database.save_draft(email_id, draft)
    
    return draft

# --- TEST BLOCK ---
if __name__ == "__main__":
    # Run this file directly to test the whole pipeline without the UI
    process_all_emails()
