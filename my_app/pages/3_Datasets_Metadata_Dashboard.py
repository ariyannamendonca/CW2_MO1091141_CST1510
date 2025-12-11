import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

import pandas as pd
import streamlit as st
from app.data.db import connect_database
from app.data.datasets import get_all_datasets, insert_dataset, update_dataset_rows_columns, delete_dataset
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Datasets Metadata Dashboard",
    page_icon="📈",
    layout="wide",
)

conn = connect_database()

st.title("Datasets Metadata Dashboard")

tab_dashboard, tab_ai = st.tabs(["Manage Dataset Metadata", "Data Science AI Assistant"])

with tab_dashboard:
    datasets = get_all_datasets(conn)
    st.dataframe(datasets, use_container_width=True)

st.header("Add New Dataset")

with st.form("new_dataset_metadata"):
    name = st.text_input("Enter dataset name")
    category = st.selectbox("Category", ["Data", "Cyber", "IT", "Other"])
    uploaded_by = st.text_input("Enter uploaded by")
    uploaded_date = st.text_input("Date uploaded")
    rows = st.text_input("Enter rows")
    columns = st.text_input("Enter columns")
    file_size_mb = st.text_input("Enter file size")
    created_at = st.date_input("Date created")
    submitted = st.form_submit_button("Add Dataset")

if submitted:
    insert_dataset(conn, name, category, uploaded_by, uploaded_date, rows, columns, file_size_mb, created_at)
    st.success("Dataset added successfully!")
    st.rerun()

st.header("Update Dataset_Metadata")

dataset_ids = datasets['dataset_id'].tolist() if not datasets.empty and 'dataset_id' in datasets.columns else []

with st.form("update_form", clear_on_submit=True):
    col1, col2, col3, col4 = st.columns([1, 1, 1, 0.7])

    with col1:
        upd_id = st.selectbox("Dataset ID:", dataset_ids, help="Select Dataset ID you want to modify.")

    with col2:
        upd_rows = st.number_input("New Row Count:", min_value=0, step=1, help="Enter updated number of rows.")

    with col3:
        upd_columns = st.number_input("New Column Count:", min_value=1, step=1, help="Enter updated number of columns.")

    with col4:
        st.write(" ")
        update_submitted = st.form_submit_button("Update Dimensions")

    if update_submitted:
        if upd_id:
            rows_affected = update_dataset_rows_columns(conn, upd_id, upd_rows, upd_columns)

            if rows_affected > 0:
                st.success(f"Rows and Columns for Dataset ID **{upd_id}** has been updated to.")
                st.rerun()
            else:
                st.warning(f"Dataset ID **{upd_id}** was not found or values are already the same.")
        else:
            st.error("Please select a Dataset ID to update.")

st.header("Delete Dataset")

with st.form("delete_dataset"):
    del_id = st.number_input("Dataset ID to Delete", step=1)
    del_submit = st.form_submit_button("Delete Dataset")

if del_submit and del_id:
    rows = delete_dataset(conn, del_id)
    if rows:
        st.success(f"Dataset **{del_id}** has been deleted.")
    else:
        st.error("Dataset **{del_id}** was not found.")
    st.rerun()

st.title("Dataset Metadata Charts")
st.header("Visualising Dataset Metrics")

datasets = get_all_datasets(conn)

if datasets.empty:
    st.warning("No Datasets found!")
else:
    datasets['upload_date'] = pd.to_datetime(datasets['upload_date'], errors='coerce')
    datasets.dropna(subset = ['upload_date'], inplace = True)

    st.subheader("Line Chart: Datasets uploaded Over Time")

    datasets_by_day = (
        datasets.groupby(datasets['upload_date'].dt.date)
        .size()
        .reset_index(name='Count')
        .rename(columns={'upload_date': 'date'})
    )

    datasets_by_day['date'] = pd.to_datetime(datasets_by_day['date'])
    datasets_by_day.set_index('date', inplace=True)

    st.line_chart(datasets_by_day['Count'])

    st.divider()

    st.subheader("Bar Chart: Arranged by who uploaded them")

    category_counts = datasets['uploaded_by'].value_counts().reset_index()
    category_counts.columns = ['uploaded by', 'Count']

    st.bar_chart(category_counts.set_index('uploaded by'))

    st.divider()

#Data Science AI Assistant
def datascience_assistant():
    SYSTEM_PROMPT_CONTENT = """You are a data science expert assistant.
    - Help users understand and make datasets for analysis or production.
    - Provide technical guidance.
    - Evaluate data quality.
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

    st.title("🛡️ Data Science AI Assistant")
    st.caption("Powered by Google Gemini")

    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "user", "content": SYSTEM_PROMPT_CONTENT},
            {"role": "model", "content": "I am ready to help you with my expertise in Data Science."}
        ]

    st.subheader("Chat Controls")
    message_count = len(st.session_state.messages) - 1
    st.metric("Messages", message_count)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "user", "content": SYSTEM_PROMPT_CONTENT},
            {"role": "model", "content": "I am ready to help you with my expertise in Data Science."}
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

    prompt = st.chat_input("Ask about data science...")

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
    datascience_assistant()