import os
import json
from dotenv import load_dotenv

# pip install -U google-generativeai python-dotenv
try:
    import google.generativeai as genai
    _HAS_GENAI = True
except Exception:
    genai = None
    _HAS_GENAI = False

load_dotenv()

API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

# Use the same model as your JS project for consistency
MODEL_NAME = os.getenv("GOOGLE_GEMINI_MODEL", "gemini-pro-latest")

if _HAS_GENAI and API_KEY:
    try:
        genai.configure(api_key=API_KEY)
    except Exception:
        # Don't crash at import-time; handle at call-time
        pass

def _build_model(json_mode: bool):
    if not _HAS_GENAI:
        raise RuntimeError(
            "google-generativeai is not installed. Run: pip install -U google-generativeai"
        )
    if not API_KEY:
        raise RuntimeError(
            "GOOGLE_GEMINI_API_KEY not set. Put it in your environment or .env"
        )
    generation_config = None
    if json_mode:
        # This tells Gemini to return a JSON string
        generation_config = {"response_mime_type": "application/json"}
    return genai.GenerativeModel(model_name=MODEL_NAME), generation_config

def get_llm_response(prompt_text, json_mode=False):
    """
    Sends a prompt to Gemini and returns text (str) or parsed JSON (dict/list).
    """
    try:
        model, generation_config = _build_model(json_mode=json_mode)
        resp = model.generate_content(prompt_text, generation_config=generation_config)

        # For SDK 0.7+, .text is typically the right way
        text = getattr(resp, "text", None)
        if text is None:
            # Fallback stitching if needed
            parts = []
            for cand in getattr(resp, "candidates", []) or []:
                content = getattr(cand, "content", None)
                for p in getattr(content, "parts", []) or []:
                    if hasattr(p, "text") and p.text:
                        parts.append(p.text)
            text = "".join(parts)

        if not text:
            return {} if json_mode else ""

        if json_mode:
            # Be strict: require valid JSON (array/object)
            return json.loads(text)
        else:
            return text.strip()

    except Exception as e:
        print(f"Error calling Gemini / Generative AI API: {e}")
        return {} if json_mode else "Error generating response."

if __name__ == "__main__":
    print("Testing Text Mode...")
    print(get_llm_response("Explain quantum computing in one sentence."))

    print("\nTesting JSON Mode...")
    json_prompt = (
        "Extract tasks from this email: "
        "'Hi, please submit the report by Friday and call mom.'\n"
        "Return ONLY a JSON array. Each item must have 'task' and 'deadline'."
    )
    print(get_llm_response(json_prompt, json_mode=True))

