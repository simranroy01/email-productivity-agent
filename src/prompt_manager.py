from src import database

# Define the keys used in the system to prevent typos
PROMPT_TYPES = ["categorization", "action_items", "auto_reply"]

def get_all_prompts():
    """
    Retrieves all active prompts to display in the 'Brain' settings panel.
    Returns a dictionary: { 'categorization': '...', 'action_items': '...' }
    """
    prompts = {}
    for key in PROMPT_TYPES:
        prompts[key] = database.get_prompt(key)
    return prompts

def update_prompt(key, new_text):
    """
    Validates and saves a new prompt.
    
    Args:
        key (str): The prompt type (must be in PROMPT_TYPES).
        new_text (str): The new prompt template.
        
    Returns:
        (bool, str): Success status and a message for the UI.
    """
    if key not in PROMPT_TYPES:
        return False, f"Invalid prompt type: {key}"
    
    if not new_text or len(new_text.strip()) < 10:
        return False, "Prompt is too short. Please provide detailed instructions."
        
    try:
        database.update_prompt_in_db(key, new_text)
        return True, f"Successfully updated {key} logic."
    except Exception as e:
        return False, f"Database Error: {e}"

def reset_defaults():
    """
    Resets all prompts to the system defaults. 
    Useful if the user breaks the agent with bad prompts.
    """
    database.seed_prompts()
    return "System brain reset to factory defaults."
