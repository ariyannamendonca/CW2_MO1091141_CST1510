import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

import streamlit as st
from app.data.db import connect_database
from app.data.incidents import get_all_incidents, insert_incident

conn = connect_database()

st.title("Cyber Incidents Dashboard")

incidents = get_all_incidents(conn)
st.dataframe(incidents, use_container_width=True)

with st.form("new_incident"):
    date = st.date_input("Date of incident")
    category = st.text_input("Category")
    severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
    status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
    description = st.text_input("Description")
    reported_by = st.text_input("Reported by")
    submitted = st.form_submit_button("Add Incident")

if submitted:
    insert_incident(conn, str(date), category, severity, status, description, reported_by)
    st.success("Incident Added Successfully!")
    st.rerun()