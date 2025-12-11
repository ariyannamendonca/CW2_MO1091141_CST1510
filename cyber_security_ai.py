import streamlit as st
from google import genai
from google.genai import types

def cybersecurity_assistant():
    SYSTEM_PROMPT_CONTENT = """You are a cybersecurity expert assistant.
    - Analyse incidents and threats.
    - Provide technical guidance.
    - Explain attack vectors and mitigation.
    - Use standard terminology (MITRE ATTACK,CVE).
    - Prioritise actionable recommendations. 
    Tone: Professional, technical .
    Format: Clear, structured responses"""

    model = "gemini-2.5-flash"

    try:
        if "GEMINI_API_KEY" not in st.secrets:
            st.error("Error: GEMINI API KEY not found in streamlit secrets.toml.")
            st.stop()

        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception as e:
        st.error(e)
        return

    st.title("🛡️ Cybersecurity AI Assistant")
    st.caption("Powered by Google Gemini")

    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "user", "content": SYSTEM_PROMPT_CONTENT},
            {"role": "model", "content": "I am ready to help you with my expertise in cyber security."}
        ]

    st.subheader("Chat Controls")
    message_count = len(st.session_state.messages) - 1
    st.metric("Messages", message_count)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "user", "content": SYSTEM_PROMPT_CONTENT},
            {"role": "model", "content": "I am ready to help you with my expertise in cyber security."}
        ]
        st.rerun()

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher values make output more creative/random"
    )

    config = types.GenerateContentConfig(temperature=temperature)

    for i, message in enumerate(st.session_state.messages):
        if i > 0:
            display_role = "assistant" if message ["role"] == "model" else message["role"]
            with st.chat_message(display_role):
                st.markdown(message["content"])

    prompt = st.chat_input("Ask about cybersecurity...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

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
            with st.spinner(f"Analyzing using {model}..."):
                response_stream = client.models.generate_content_stream(
                    model=model,
                    contents=gemini_contents,
                    config=config
                )

            with st.chat_message("assistant"):
                container = st.empty()
                full_reply = ""

                for chunk in response_stream:
                    full_reply += chunk.text
                    container.markdown(full_reply + "")

                container.markdown(full_reply)

            st.session_state.messages.append({
                "role":"assistant",
                "content":full_reply
            })

        except Exception as e:
            st.error(f"An error occurred while calling the API: {e}")
