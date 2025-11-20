import streamlit as st
import time
import json
import pandas as pd
from src import database, email_processor, prompt_manager, llm_service

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Email Productivity Agent",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR POLISH ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
    }
    .category-badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        color: white;
        font-size: 0.8em;
    }
    /* Badge Colors */
    .badge-Meeting { background-color: #3b82f6; }       /* Blue */
    .badge-Task { background-color: #ef4444; }          /* Red */
    .badge-Newsletter { background-color: #10b981; }    /* Green */
    .badge-Spam { background-color: #6b7280; }          /* Gray */
    .badge-Project { background-color: #f59e0b; }       /* Amber for Project Update */
    .badge-Uncategorized { background-color: #9ca3af; } /* Light Gray for Unprocessed */
    
    .email-card {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        background-color: #ffffff;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your Email Productivity Agent. I've analyzed your inbox. Ask me anything, like 'What tasks are due soon?' or 'Summarize the email from Maya'."}
    ]

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("📧 Agent Controls")
    
    st.markdown("### ⚙️ Ingestion Pipeline")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Load Inbox"):
            with st.spinner("Loading mock data..."):
                database.load_mock_data()
            st.success("Inbox Loaded!")
            time.sleep(1)
            st.rerun()
            
    with col2:
        if st.button("🧠 Process AI"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(current, message):
                progress_bar.progress(current)
                status_text.text(message)
                
            email_processor.process_all_emails(progress_callback=update_progress)
            time.sleep(1)
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Inbox Stats")
    emails = database.fetch_emails()
    
    # Calculate stats safely
    total_emails = len(emails)
    
    # Handle None values safely for counting
    task_count = sum(1 for e in emails if e['category'] == 'Task')
    meeting_count = sum(1 for e in emails if e['category'] == 'Meeting')
    
    st.metric("Total Emails", total_emails)
    col_a, col_b = st.columns(2)
    col_a.metric("Tasks", task_count)
    col_b.metric("Meetings", meeting_count)
    
    st.markdown("---")
    if st.button("🗑️ Reset System"):
        # For demo purposes, we might want to clear DB
        # Here we just reset prompts as a safe default
        prompt_manager.reset_defaults()
        st.warning("Prompts reset to default.")

# --- MAIN TABS ---
tab_inbox, tab_brain, tab_agent = st.tabs(["📬 Smart Inbox", "🧠 Agent Brain", "🤖 Email Agent"])

# === TAB 1: SMART INBOX ===
with tab_inbox:
    st.header("Smart Inbox")
    
    # Filters
    filter_col1, filter_col2 = st.columns([1, 3])
    with filter_col1:
        category_filter = st.selectbox("Filter by Category", ["All", "Task", "Meeting", "Newsletter", "Project Update", "Spam", "Uncategorized"])
    
    # Display Emails
    for email in emails:
        # FIX: Handle NoneType category (if AI hasn't run yet)
        current_category = email['category'] if email['category'] else "Uncategorized"

        # Apply Filter
        if category_filter != "All" and current_category != category_filter:
            continue
            
        # Badge Logic
        # Only split if category is a string, safe because of the fix above
        cat_clean = current_category.split(" ")[0] # Handle 'Project Update' -> 'Project' for CSS
        badge_html = f'<span class="category-badge badge-{cat_clean}">{current_category}</span>'
        
        # Card Layout
        with st.container():
            col_exp, col_act = st.columns([5, 1])
            
            with col_exp:
                with st.expander(f"{email['sender']} | {email['subject']}"):
                    st.markdown(f"**Received:** {email['received_date']} &nbsp; {badge_html}", unsafe_allow_html=True)
                    st.markdown("---")
                    st.write(email['body'])
                    
                    # Show Extracted Actions if any
                    if email['action_items']:
                        try:
                            actions = json.loads(email['action_items'])
                            if actions.get('tasks'):
                                st.warning("📋 **Action Items Detected:**")
                                for task in actions['tasks']:
                                    st.markdown(f"- {task.get('description')} (Due: {task.get('deadline', 'N/A')})")
                        except:
                            pass
                    
                    # Show Draft if exists
                    # Show Draft if exists (EDITABLE VERSION)
                    if email['is_drafted']:
                        st.markdown("#### 📝 Draft Reply")
                        # Text area allows user to edit the LLM's output
                        edited_draft = st.text_area(
                            label="Review and Edit:",
                            value=email['reply_draft'],
                            height=150,
                            key=f"draft_area_{email['id']}"
                        )
                        
                        # Button to save the user's manual edits
                        if st.button("💾 Save Edits", key=f"save_{email['id']}"):
                            database.save_draft(email['id'], edited_draft)
                            st.success("Draft updated locally!")
                            time.sleep(0.5)
                            st.rerun()

            with col_act:
                # "Draft Reply" Action
                if st.button("Draft Reply", key=f"btn_{email['id']}"):
                    with st.spinner("Generating draft..."):
                        draft = email_processor.generate_reply(email['id'])
                    st.success("Draft saved!")
                    time.sleep(0.5)
                    st.rerun()

# === TAB 2: AGENT BRAIN ===
with tab_brain:
    st.header("⚙️ Configure Agent Logic")
    st.info("Edit these prompts to change how the AI processes your emails. This demonstrates the 'Prompt-Driven' architecture.")
    
    current_prompts = prompt_manager.get_all_prompts()
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.subheader("🏷️ Categorization Logic")
        cat_prompt = st.text_area("Instructions for classifying emails:", 
                                  value=current_prompts.get('categorization', ''), height=200)
        if st.button("Save Category Prompt"):
            success, msg = prompt_manager.update_prompt('categorization', cat_prompt)
            if success: st.success(msg)
            else: st.error(msg)

    with col_p2:
        st.subheader("📋 Action Item Logic")
        act_prompt = st.text_area("Instructions for extracting tasks:", 
                                  value=current_prompts.get('action_items', ''), height=200)
        if st.button("Save Action Prompt"):
            success, msg = prompt_manager.update_prompt('action_items', act_prompt)
            if success: st.success(msg)
            else: st.error(msg)
            
    st.subheader("✍️ Auto-Reply Style")
    reply_prompt = st.text_area("Define the persona and tone for replies:", 
                                value=current_prompts.get('auto_reply', ''), height=150)
    if st.button("Save Reply Prompt"):
        success, msg = prompt_manager.update_prompt('auto_reply', reply_prompt)
        if success: st.success(msg)
        else: st.error(msg)

# === TAB 3: EMAIL AGENT (CHAT) ===
with tab_agent:
    st.header("🤖 Chat with your Inbox")
    
    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask about your emails..."):
        # 1. User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Agent Logic (Simple RAG)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Fetch recent emails as context
                # In a real app, this would be a vector search. 
                # For this assignment, we dump the last 10 emails as text context.
                recent_emails = emails[:10] 
                context_str = ""
                for e in recent_emails:
                    # Handle None values in context construction as well
                    c_cat = e['category'] if e['category'] else "Uncategorized"
                    context_str += f"From: {e['sender']}, Subj: {e['subject']}, Category: {c_cat}, Body: {e['body']}\n\n"
                
                full_query = f"""
                User Query: {prompt}
                
                Context (Your Inbox Data):
                {context_str}
                
                Answer the user's question based ONLY on the inbox context provided above.
                If asked to draft a reply, write the draft text.
                """
                
                response = llm_service.get_llm_response(full_query)
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
