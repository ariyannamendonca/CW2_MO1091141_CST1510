import sys
import os
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from app.data.db import connect_database
from app.data.incidents import Cyberincidents
from google import genai
from google.genai import types

#Ensure state keys exist in case user opens this page first
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

#if not logged in send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the Cyber Incidents Dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

st.set_page_config(
    page_title="Cyber Incidents Dashboard",
    page_icon="🚨",
    layout="wide",
)

conn = connect_database()
cyber_incidents = Cyberincidents(conn)

st.title("Cyber Incidents Dashboard")

tab_dashboard, tab_ai = st.tabs(["Manage Cyber Incidents", "Cybersecurity AI Assistant"])

with tab_dashboard:
    incidents = cyber_incidents.get_all_incidents()
    st.dataframe(incidents, use_container_width=True)

    st.header("Add New Incident")
    with st.form("new_incident"):
        date = st.date_input("Date of incident")
        category = st.text_input("Category")
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
        description = st.text_input("Description")
        reported_by = st.text_input("Reported by")
        submitted = st.form_submit_button("Add Incident")

    if submitted:
        new_incident_id = cyber_incidents.insert_incident(str(date), category, severity, status, description, reported_by)

        if new_incident_id:
            st.success("Incident Added Successfully!")
        else:
            st.error("Could not add incident!")

    st.header("Update Incident Status")
    incidents_ids = incidents['incident_id'].tolist() if not incidents.empty else[]
    status_options = ["Open", "In Progress", "Resolved"]

    with st.form("update_status_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([1,1, 0.7])

        with col1:
            upd_id = st.selectbox("Incident ID:", incidents_ids, help="Select Incident ID you want to modify.")

        with col2:
            upd_status = st.selectbox("New Status:", status_options, help="Choose new status for the selected incident.")

        with col3:
            st.write(" ")
            update_submitted = st.form_submit_button("Update Status")

        if update_submitted:
            if upd_id:
                rows_affected = cyber_incidents.update_incident_status(upd_id, upd_status)

                if rows_affected > 0:
                    st.success(f"Status for Incident ID **{upd_id}** has been updated to **{upd_status}**.")
                    st.rerun()
                else:
                    st.warning(f"Incident ID **{upd_id}** was not found or status is already set to **{upd_status}**.")
            else:
                st.error("Please select an incident ID to update.")

    st.header("Delete Incident")
    with st.form("delete_incident"):
        del_id = st.number_input("Incident ID to Delete", step=1)
        del_submit = st.form_submit_button("Delete Incident")

    if del_submit and del_id:
        rows = cyber_incidents.delete_incident_status(del_id)
        if rows:
            st.success(f"Incident **{del_id}** has been deleted.")
        else:
            st.error("Incident **{del_id}** was not found.")
        st.rerun()

    try:
        incidents = cyber_incidents.get_all_incidents()
    except Exception as e:
        st.error(f"Error loading incidents for charts: {e}")
        incidents = pd.DataFrame()

    st.title ("Cyber Incident Bar Chart")
    st.header("Visualising Key Incident Metrics:")

    if incidents.empty:
        st.warning("No Incidents found to display charts!")
    else:
        try:
            incidents['created_at'] = pd.to_datetime(incidents['created_at'], errors='coerce')
            incidents.dropna(subset = ['created_at'], inplace = True)
        except Exception as e:
            st.error(f"ERROR converting 'created_at' column: {e}")
            st.stop()

        category_counts = incidents['category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']

        st.divider()

        st.header("Incident by Category")
        st.bar_chart(category_counts.set_index('Category'))

#Cybersecurity AI Assistant
def cybersecurity_assistant():
    SYSTEM_PROMPT_CONTENT = """You are a cybersecurity expert assistant.
    - Analyse incidents and threats.
    - Provide technical guidance.
    - Explain attack vectors and mitigation.
    - Use standard terminology (MITRE ATTACK,CVE).
    - Prioritise actionable recommendations. 
    Tone: Professional, technical .
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

    st.title("🛡️ Cybersecurity AI Assistant")
    st.caption("Powered by Google Gemini")

    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "user", "content": SYSTEM_PROMPT_CONTENT},
            {"role": "model", "content": "I am ready to help you with my expertise in cyber security."}
        ]

    st.subheader("Chat Controls")
    message_count = len(st.session_state.messages) - 1
    st.metric("Messages", message_count)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "user", "content": SYSTEM_PROMPT_CONTENT},
            {"role": "model", "content": "I am ready to help you with my expertise in cyber security."}
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

    prompt = st.chat_input("Ask about cybersecurity...")

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
    cybersecurity_assistant()