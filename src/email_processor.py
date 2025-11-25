import json
import time
import os
import concurrent.futures
from typing import Optional
from src import database
from src import llm_service

def process_all_emails(progress_callback=None, max_workers: Optional[int] = None):
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

    # allow callers to override workers; default to env or 4
    if max_workers is None:
        try:
            max_workers = int(os.getenv("EMAIL_PROCESSOR_WORKERS", "4"))
        except Exception:
            max_workers = 4

    # Worker function for a single email -- isolates per-email work so we can run in parallel
    def _process_one(email_item):
        email_id = email_item['id']
        sender = email_item['sender']
        body = email_item['body']

        # --- STEP 1: CATEGORIZATION ---
        try:
            full_cat_prompt = f"{cat_prompt_template}\n\nEMAIL BODY:\n{body}"
            category = llm_service.get_llm_response(full_cat_prompt, json_mode=False)
            category = category.replace("Category:", "").strip().strip(".")
        except Exception as e:
            print(f"Error categorizing email {email_id}: {e}")
            category = "Uncategorized"

        # --- STEP 2: ACTION ITEM EXTRACTION ---
        action_data = {"tasks": []}
        if category not in ["Spam", "Newsletter"]:
            try:
                full_action_prompt = f"{action_prompt_template}\n\nEMAIL BODY:\n{body}"
                action_data = llm_service.get_llm_response(full_action_prompt, json_mode=True)
                if not isinstance(action_data, dict) or 'tasks' not in action_data:
                    action_data = {"tasks": []}
            except Exception as e:
                print(f"Error extracting actions for {email_id}: {e}")

        # Save results
        database.update_email_analysis(
            email_id=email_id,
            category=category,
            action_items=action_data
        )

        return email_id, sender, category, action_data

    # Use a ThreadPoolExecutor to parallelize LLM calls across emails
    completed_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        # Submit all jobs
        future_to_email = {ex.submit(_process_one, e): e for e in emails}

        for fut in concurrent.futures.as_completed(future_to_email):
            try:
                email_id, sender, category, action_data = fut.result()
                completed_count += 1
                print(f"Processed {email_id}: [{category}] - Found {len(action_data.get('tasks', []))} tasks")

            except Exception as e:
                # Unexpected error for individual item; don't stop processing
                completed_count += 1
                failed_email = getattr(fut, 'email', None)
                print(f"Error processing email (future): {e}")

            # UI progress update after each completed future
            if progress_callback:
                progress_callback(completed_count / total, f"Processed {completed_count} / {total} emails...")

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
