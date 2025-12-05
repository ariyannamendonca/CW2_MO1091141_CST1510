import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

import streamlit as st
import pandas as pd
import numpy as np
from app.data.db import connect_database
from app.data.incidents import get_all_incidents

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

#if logged in, show dashboard
conn = connect_database()
incidents = get_all_incidents(conn)
st.title("📊Dashboard")
st.success(f"Hello, **{st.session_state.username}!** You are logged in.")

st.dataframe(incidents, use_container_width = True)

#Logout button
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")

#check is user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.error("You must be logged in to view the dashboard.")
        st.switch_page("Home.py")
    st.stop()
