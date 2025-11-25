import datetime
from src.database import get_connection, MOCK_DATA_PATH
from src.llm_service import get_llm_response
import os
import json
import random
def generate_and_insert_ai_emails(num_emails=20):
    """Generate up to `num_emails` messages and insert them into the DB.

    - Calls the LLM (Gemini / Google Generative AI) to produce a JSON array of email-like objects.
    - Sanitizes repeated paragraphs and deduplicates repeated sequences.
    - If an LLM-produced single email body includes multiple salutations (looks like multiple emails merged), split into separate entries.
    - Ensures the inserted row is unprocessed (category/action_items left blank) so the processing step runs only when the user clicks "Process AI".
    """

    prompt = f"""
Generate exactly {num_emails} emails divided among these types with roughly equal distribution.
Each email should be realistic and detailed prose (not bullet points).

TYPES:
1. To-Do / Task Requests (explicit actions with deadlines).
2. Meeting Requests (include time, date, topic).
3. Newsletters / Informational Updates (no actions; long body).

Each email must be a JSON object with EXACTLY these fields:
- sender (string)
- subject (string)
- body (string)
- received_date (ISO 8601 string)
- category (one of: "Task", "Meeting", "Newsletter", "Spam")

Return ONLY a JSON array of email objects. No extra text, no markdown.
"""


    def _sanitize_body(text: str) -> str:
        # Normalize and deduplicate paragraphs; remove consecutive duplicates and keep first occurrence only
        if not isinstance(text, str):
            return text

        normalized = text.replace('\r\n', '\n').strip()
        paragraphs = [p.strip() for p in normalized.split('\n\n') if p.strip()]

        # Remove consecutive duplicate paragraphs
        cleaned = []
        last = None
        for p in paragraphs:
            if p == last:
                continue
            cleaned.append(p)
            last = p

        # Remove duplicate paragraphs globally while preserving order
        seen = set()
        unique = []
        for p in cleaned:
            if p in seen:
                continue
            seen.add(p)
            unique.append(p)

        return "\n\n".join(unique)

    # Call LLM
    try:
        ai_emails = get_llm_response(prompt, json_mode=True)
    except Exception as e:
        print(f"Error generating AI emails from LLM: {e}")
        ai_emails = None

    # Fallback
    if not isinstance(ai_emails, list):
        if os.path.exists(MOCK_DATA_PATH):
            with open(MOCK_DATA_PATH, 'r', encoding='utf-8') as f:
                try:
                    ai_emails = json.load(f)
                except Exception as e:
                    print('Failed to load local mock:', e)
                    ai_emails = []
        else:
            ai_emails = []

    # Expand combined emails (split by salutations if multiple present)
    expanded = []
    for item in ai_emails:
        if not isinstance(item, dict):
            continue
        body_raw = (item.get('body') or '')
        paras = [p.strip() for p in body_raw.split('\n\n') if p.strip()]
        salutation_idx = [i for i, p in enumerate(paras) if p.lower().startswith(('hi ', 'hello ', 'dear '))]
        if len(salutation_idx) <= 1:
            expanded.append(item)
            continue

        # split into separate email-like chunks
        splits = salutation_idx + [len(paras)]
        for i in range(len(salutation_idx)):
            s = splits[i]
            e = splits[i+1]
            chunk_paras = paras[s:e]
            new_item = dict(item)
            new_item['body'] = '\n\n'.join(chunk_paras)
            new_item['subject'] = (item.get('subject') or '') + ' | piece'
            expanded.append(new_item)

    # randomize and cap
    random.shuffle(expanded)
    ai_emails = expanded[:num_emails]

    conn = get_connection()
    cursor = conn.cursor()

    # (no debug logging)
    inserted_count = 0
    for email in ai_emails:
        if not isinstance(email, dict):
            continue
        try:
            sender = email.get('sender', 'unknown@example.com')
            subject = email.get('subject', '')
            # insert
            body = email.get('body', '') or ''

            # Do not add programmatic filler. We ask the LLM to produce naturally detailed bodies in the prompt
            # and we only sanitize/remove duplicates. If the LLM returns a short body we will keep it (no synthetic filler).

            # sanitize repeated paragraphs (remove exact duplicates)
            body = _sanitize_body(body)

            # ensure the email is unprocessed on load
            received_date = email.get('received_date') or datetime.datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO emails (sender, subject, body, received_date, category, summary, action_items)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (sender, subject, body, received_date, None, None, None))
            inserted_count += 1
            # inserted
        except Exception as exc:
            print('Error inserting email:', exc)
            continue

    conn.commit()
    conn.close()
    print(f'Inserted {inserted_count} AI-generated emails into the database.')
    return inserted_count
