import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

import streamlit as st
from app.data.db import connect_database
from app.data.tickets import get_tickets, insert_ticket, update_tickets, delete_ticket

conn = connect_database()

st.title("IT Tickets Dashboard")

tickets = get_tickets(conn)
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
    insert_ticket(conn, ticket_id, priority, status, category, subject, description, created_date, resolved_date, resolution_time_hours, assigned_to)
    st.success("Ticket Added Successfully!")
    st.rerun()

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
            rows_affected = update_tickets(conn, upd_id, upd_status)

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
    rows = delete_ticket(conn, del_id)
    if rows:
        st.success(f"Ticket **{del_id}** has been deleted.")
    else:
        st.error("Ticket **{del_id}** was not found.")
    st.rerun()

if st.button("Back to Main Dashboard"):
    st.switch_page("pages/1_Dashboard.py")