# Email Agent

An AI-powered email processing agent that categorizes and extracts information from emails using LLM.

## Features

- Categorize emails automatically
- Extract key information
- Streamlit-based UI

## Setup

1. Install dependencies: `pip install -r requirements.txt`

If you plan to use the Google Gemini / Generative AI integration, ensure the client package is installed and up-to-date:

```powershell
pip install --upgrade google-generative-ai
```

If you get an error like "module 'google.generativeai' has no attribute 'responses'", it's usually because:

- the `google-generative-ai` package isn't installed correctly in your environment, or
- an older/newer release of the package exposes a different API surface.

Try upgrading the package or reinstalling it in the environment you're running Streamlit from (same interpreter/environment). If pip fails with a network or permission error, check your connection and environment.

### Troubleshooting the google.generativeai client

If you still see errors like "Installed google.generativeai package doesn't expose a supported API surface", use the included helper to inspect the installed package and confirm the available API surfaces:

```powershell
python src/check_genai.py
```

The script will attempt to import `google.generativeai`, print the version if present, list top-level attributes, and indicate whether `chat` and `responses` are available. If neither exists, upgrade the client:

```powershell
python -m pip install --upgrade google-generative-ai
```

Make sure to run the commands inside the same Python environment used to start Streamlit (e.g., the same virtualenv or conda env).
2. Set your Gemini / Google Generative AI API key in `.env` as `GOOGLE_GEMINI_API_KEY` (used to generate AI emails when clicking "Load Inbox"). Do NOT commit your API key into source control — store it in a `.env` file or your environment. If not set, the app falls back to pre-generated mock data.
3. Run the app: `streamlit run app.py`

## Project Structure

- `assets/`: Mock data
- `data/`: SQLite database
- `src/`: Source code
  - `database.py`: Database models
  - `llm_service.py`: Gemini / Google Generative AI LLM integration (uses `GOOGLE_GEMINI_API_KEY`)
  - `prompt_manager.py`: Prompt management
  - `email_processor.py`: Email processing logic
- `app.py`: Main UI
