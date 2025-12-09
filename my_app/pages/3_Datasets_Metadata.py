import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

import streamlit as st
from app.data.db import connect_database
from app.data.datasets import get_all_datasets, insert_dataset

conn = connect_database()

st.title("Datasets Metadata Dashboard")

datasets = get_all_datasets(conn)
st.dataframe(datasets, use_container_width=True)

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
