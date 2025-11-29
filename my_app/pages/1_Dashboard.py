import streamlit as st
import pandas as pd
import numpy as np

from app.data.db import connect_database
from app.data.incidents import get_all_incidents, insert_incident
from app.data.datasets import get_all_datasets
from app.data.tickets import get_tickets

conn = connect_database('DATA/intelligence_platform.db')

incidents = get_all_incidents(conn)
datasets = get_all_datasets(conn)
tickets = get_tickets(conn)

st.title("Cyber incidents Dashboard")

incident = get_all_incidents(conn)
st.dataframe(incidents, use_container_width=True)

with st.form("new_incident"):
    title = st.text_input("Incident Title")
    severity = st.selectbox("Severity", ["Low", "Medium", "High, Critical"])
    status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])

    submitted = st.form_submit_button("Add Incident")

    if submitted and title:
        insert_incident(conn, title, severity, status)
        st.success("Incident added successfully")
        st.rerun()

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

#Ensure state keys exist in case user opens this page first
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

#if not logged in send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

#if logged in show dashboard
st.title("📊 Dashboard")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

st.caption("Welcome Back!")

#Sidebar filters
with st.sidebar:
    st.header("Filters")
    n_points = st.slider("Number of data points", 10, 200, 50)

#Fake data
data = pd.DataFrame(
    np.random.rand(n_points, 3),
    columns=["A", "B", "C"],
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Line chart")
    st.line_chart(data)

with col2:
    st.subheader("Bar chart")
    st.bar_chart(data)

with st.expander("See raw data"):
    st.dataframe(data)

#Logout button
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")

#check is user is logged in
if not st.session_state.logged_in:
    st.error("You must be logged in...")
    st.switch_page("Home.py")
