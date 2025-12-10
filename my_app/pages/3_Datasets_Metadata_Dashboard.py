import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

import pandas as pd
import streamlit as st
from app.data.db import connect_database
from app.data.datasets import get_all_datasets, insert_dataset, update_dataset_rows_columns, delete_dataset

conn = connect_database()

st.title("Datasets Metadata Dashboard")

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

if st.button("Back to Main Dashboard"):
    st.switch_page("pages/1_Dashboard.py")