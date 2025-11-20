# Email Agent

An AI-powered email processing agent that categorizes and extracts information from emails using LLM.

## Features

- Categorize emails automatically
- Extract key information
- Streamlit-based UI

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set up your OpenAI API key in `.env`
3. Run the app: `streamlit run app.py`

## Project Structure

- `assets/`: Mock data
- `data/`: SQLite database
- `src/`: Source code
  - `database.py`: Database models
  - `llm_service.py`: OpenAI integration
  - `prompt_manager.py`: Prompt management
  - `email_processor.py`: Email processing logic
- `app.py`: Main UI
