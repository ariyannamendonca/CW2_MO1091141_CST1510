import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

import pandas as pd
import streamlit as st
from app.data.db import connect_database
from app.data.incidents import get_all_incidents, insert_incident, update_incident_status, delete_incident_status

conn = connect_database()

st.title("Cyber Incidents Dashboard")

incidents = get_all_incidents(conn)
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
    insert_incident(conn, str(date), category, severity, status, description, reported_by)
    st.success("Incident Added Successfully!")
    st.rerun()

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
            rows_affected = update_incident_status(conn, upd_id, upd_status)

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
    rows = delete_incident_status(conn, del_id)
    if rows:
        st.success(f"Incident **{del_id}** has been deleted.")
    else:
        st.error("Incident **{del_id}** was not found.")
    st.rerun()


try:
    incidents = get_all_incidents(conn)
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

if st.button("Back to Main Dashboard"):
    st.switch_page("pages/1_Dashboard.py")