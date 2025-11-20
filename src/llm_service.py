import os
import json
import groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_NAME = "openai/gpt-oss-20b"

def get_llm_response(prompt_text, json_mode=False):
    """
    Sends a prompt to Groq and returns the response.
    
    Args:
        prompt_text (str): The user's prompt.
        json_mode (bool): If True, forces the model to return valid JSON.
    
    Returns:
        str or dict: The text response or a parsed JSON dictionary.
    """
    try:
        # Configure response format
        response_format = {"type": "json_object"} if json_mode else None

        chat_completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt_text}],
            temperature=0.7,
            response_format=response_format
        )

        response_text = chat_completion.choices[0].message.content

        # Handle the response
        if json_mode:
            # Groq returns a JSON string; we parse it into a Python dict
            return json.loads(response_text)
        else:
            return response_text.strip()

    except Exception as e:
        print(f"Error calling Groq API: {e}")
        # Return a safe fallback so the app doesn't crash
        return {} if json_mode else "Error generating response."

# --- TEST FUNCTION (Run this file directly to test) ---
if __name__ == "__main__":
    # Test 1: Regular Text
    print("Testing Text Mode...")
    print(get_llm_response("Explain quantum computing in one sentence."))
    
    # Test 2: JSON Mode (Crucial for your assignment)
    print("\nTesting JSON Mode...")
    json_prompt = """
    Extract tasks from this email: 'Hi, please submit the report by Friday and call mom.'
    Return a list of objects with keys: 'task', 'deadline'.
    """
    data = get_llm_response(json_prompt, json_mode=True)
    print(data) 
    # Output will be a real Python list/dict, not a string!
