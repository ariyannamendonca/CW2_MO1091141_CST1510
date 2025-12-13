import sys
import os
import pandas as pd
import streamlit as st

from google import genai
from google.genai import types

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from app.data.db import connect_database
from app.data.tickets import ITtickets

#Ensure state keys exist in case user opens this page first
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

#if not logged in send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the IT Tickets Dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

st.set_page_config(
    page_title="IT Tickets Dashboard",
    page_icon="🛠️",
    layout="wide",
)

conn = connect_database()
it_tickets = ITtickets(conn)

st.title("IT Tickets Dashboard")

tab_dashboard, tab_ai = st.tabs(["Manage IT Tickets", "IT Tickets AI Assistant"])

with tab_dashboard:
    tickets =it_tickets.get_tickets()
    st.dataframe(tickets, use_container_width=True)

    st.header("Add New Ticket")

    with st.form("New_ticket"):
        ticket_id = st.text_input("Ticket ID")
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        status = st.selectbox("Status", ["Open", "Resolved"])
        category = st.text_input("Category")
        subject = st.text_input("Subject")
        description = st.text_area("Description")
        created_date = st.text_input("Created Date")
        resolved_date = st.text_input("Resolved Date")
        resolution_time_hours = st.text_input("Resolution Time in Hours")
        assigned_to = st.text_input("Assigned To")
        submitted = st.form_submit_button("Add Ticket")

    if submitted:
        ticket_id_submitted = it_tickets.insert_ticket(ticket_id, priority, status, category, subject, description, created_date, resolved_date, resolution_time_hours, assigned_to)
        if ticket_id_submitted:
            st.success("IT Ticket successfully added!")
        else:
            st.error("Could not add ticket!")

    st.header("Update Ticket Status")
    ticket_ids = tickets['ticket_id'].tolist() if not tickets.empty else[]
    status_options = ["Open", "Waiting for User", "In Progress", "Resolved"]

    with st.form("update_status_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([1,1, 0.7])

        with col1:
            upd_id = st.selectbox("Ticket ID:", ticket_ids, help="Select Ticket ID you want to modify.")

        with col2:
            upd_status = st.selectbox("New Status:", status_options, help="Choose new status for the selected ticket.")

        with col3:
            st.write(" ")
            update_submitted = st.form_submit_button("Update Status")

        if update_submitted:
            if upd_id:
                rows_affected = it_tickets.update_tickets(upd_id, upd_status)

                if rows_affected > 0:
                    st.success(f"Status for Ticket ID **{upd_id}** has been updated to **{upd_status}**.")
                    st.rerun()
                else:
                    st.warning(f"Ticket ID **{upd_id}** was not found or status is already set to **{upd_status}**.")
            else:
                st.error("Please select a Ticket ID to update.")

    st.header("Delete Ticket")
    with st.form("delete_ticket"):
        del_id = st.number_input("Ticket ID to Delete", step=1)
        del_submit = st.form_submit_button("Delete Ticket")

    if del_submit and del_id:
        rows_deleted = it_tickets.delete_ticket(del_id)
        if rows_deleted:
            st.success(f"Ticket **{del_id}** has been deleted.")
        else:
            st.error("Ticket **{del_id}** was not found.")

    st.title("IT Tickets Charts")
    st.header("Visualising Tickets Metrics")

    tickets = it_tickets.get_tickets()
    if tickets.empty:
        st.warning("No IT Tickets found!")
    else:
        st.subheader("Bar Chart: Arranged by Priority")

        priority_counts = tickets['priority'].value_counts().reset_index()
        priority_counts.columns = ['priority', 'Count']

        st.bar_chart(priority_counts.set_index('priority'))

        st.divider()

#Data Science AI Assistant
def it_tickets_assistant():
    SYSTEM_PROMPT_CONTENT = """You are an IT Tickets assistant.
    - Help users analyse IT support tickets
    - Provide technical guidance.
    - Evaluate ticket quality and give improvements.
    - Use standard terminology.
    - Prioritise actionable recommendations. 
    Tone: Professional, technical, concise.
    Format: Clear, structured responses"""

    model = "gemini-2.5-flash"

    try:
        if "GEMINI_API_KEY" not in st.secrets:
            st.error("Error: GEMINI API KEY not found in streamlit secrets.toml.")
            st.stop()

        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception as e:
        st.error(e)
        return

    st.title("🛡️ IT Tickets AI Assistant")
    st.caption("Powered by Google Gemini")

    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "user", "content": SYSTEM_PROMPT_CONTENT},
            {"role": "model", "content": "I am ready to help you with my expertise in IT Tickets."}
        ]

    st.subheader("Chat Controls")
    message_count = len(st.session_state.messages) - 1
    st.metric("Messages", message_count)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "user", "content": SYSTEM_PROMPT_CONTENT},
            {"role": "model", "content": "I am ready to help you with my expertise in IT Tickets."}
        ]
        st.rerun()

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher values make output more creative/random"
    )

    config = types.GenerateContentConfig(temperature=temperature)

    for i, message in enumerate(st.session_state.messages):
        if i > 0:
            display_role = "assistant" if message ["role"] == "model" else message["role"]
            with st.chat_message(display_role):
                st.markdown(message["content"])

    prompt = st.chat_input("Ask about IT Tickets...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        gemini_contents = []
        for msg in st.session_state.messages:
            role_name = "model" if msg["role"] == "assistant" else msg["role"]
            if role_name in ["user", "model"]:
                gemini_contents.append(
                    types.Content(
                        role=role_name,
                        parts=[types.Part(text=msg["content"])],
                    )
                )

        try:
            with st.spinner(f"Analyzing using {model}..."):
                response_stream = client.models.generate_content_stream(
                    model=model,
                    contents=gemini_contents,
                    config=config
                )

            with st.chat_message("assistant"):
                container = st.empty()
                full_reply = ""

                for chunk in response_stream:
                    full_reply += chunk.text
                    container.markdown(full_reply + "")

                container.markdown(full_reply)

            st.session_state.messages.append({
                "role":"assistant",
                "content":full_reply
            })

        except Exception as e:
            st.error(f"An error occurred while calling the API: {e}")

if st.button("Back to Main Dashboard"):
    st.switch_page("pages/1_Dashboard.py")

with tab_ai:
    it_tickets_assistant()