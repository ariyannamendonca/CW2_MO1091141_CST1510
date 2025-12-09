import streamlit as st

st.title("Test secrets setup")

try:
    api_key = st.secrets['API_KEY']
    st.success("API key loaded successfully")
    st.write(f"Key starts with:{api_key[:10]}...")
except Exception as e:
    st.error("API key not loaded:{e}")