import streamlit as st
from google import genai
from google.genai import types

SYSTEM_PROMPT_CONTENT = "helpful"
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Error: GEMINI_API_KEY not found in streamlit secrets.toml.")
    st.stop()

st.title("Gemini with streaming")

if 'messages' not in st.session_state:
    st.session_state.messages = [
        {
            "role":"user",
            "content": SYSTEM_PROMPT_CONTENT
        },
        {
        "role":"model",
        "content": "Understood. I am ready to assist you with my expertise."
        }
    ]

for i, message in enumerate(st.session_state.messages):
    if i > 0:
        display_role = "assistant" if message ["role"] == "model" else message["role"]
        with st.chat_message(display_role):
            st.markdown(message["content"])

prompt = st.chat_input("Say something...")

if prompt:
    st.session_state.messages.append({
        "role":"user",
        "content": prompt
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
        response_stream = client.models.generate_content_stream(
            model = "gemini-2.5-flash",
            contents=gemini_contents
        )

        with st.chat_message("assistant"):
            container = st.empty()
            full_reply = ""

            for chunk in response_stream:
                full_reply += chunk.text
                container.markdown(full_reply)

        st.session_state.messages.append({
            "role":"assistant",
            "content": full_reply
        })
    except Exception as e:
        st.error(f"An error occurred while calling the API: {e}")