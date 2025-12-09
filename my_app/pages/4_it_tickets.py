import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

import streamlit as st
from app.data.db import connect_database
from app.data.tickets import get_tickets, insert_ticket

conn = connect_database()

st.title("IT Tickets Dashboard")

tickets = get_tickets(conn)
st.dataframe(tickets, use_container_width=True)

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
    insert_ticket(conn, ticket_id, priority, status, category, subject, description, created_date, resolved_date, resolution_time_hours, assigned_to)
    st.success("Ticket Added Successfully!")
    st.rerun()