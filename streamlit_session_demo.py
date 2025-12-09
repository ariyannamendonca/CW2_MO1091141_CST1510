import streamlit as st

st.title("Chat history with session state")

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Say something...")

if prompt:
    st.session_state.messages.append({
        "role":"user",
        "content":prompt
    })

with st.chat_message("user"):
    st.markdown(prompt)

ai_response = f"You said: {prompt}"

st.session_state.messages.append({
    "role":"assistant",
    "content":ai_response
})

with st.chat_message("assistant"):
    st.markdown(ai_response)