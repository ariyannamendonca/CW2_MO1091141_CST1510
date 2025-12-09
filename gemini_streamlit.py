import streamlit as st
from google import genai
from google.genai import types

try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Error: GEMINI API KEY not found in streamlit secrets.toml.")
    st.stop()

st.title("💬 Cybersecurity AI Assistant ")

if 'messages' not in st.session_state:
    st.session_state.messages = []

for messages in st.session_state.messages:
    display_role = "assistant" if messages["role"] == "model" else messages["role"]
    with st.chat_message(display_role):
        st.markdown(messages["content"])

prompt = st.chat_input("Say something...")

if prompt:
    st.session_state.messages.append({
        "role":"user",
        "content":prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

        gemini_contents = []
        for msg in st.session_state.messages:
            role_name = "model" if msg["role"] == "assistant" else msg["role"]

            if role_name in ["user", "model"]:
                gemini_contents.append(
                    types.Content(
                        role=role_name,
                        parts=[types.Part(text=msg["content"])],
                    )
                )
        try:
            response_object = client.models.generate_content(
                model = "gemini-2.5-flash",
                contents=gemini_contents
            )

            assistant_message = response_object.text
            with st.chat_message("assistant"):
                st.markdown(assistant_message)

            st.session_state.messages.append({
                "role":"assistant",
                "content":assistant_message
            })
        except Exception as e:
            st.error(f"An error occurred while calling Gemini API: {e}")