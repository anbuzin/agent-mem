import streamlit as st
import httpx

from agent_mem.common.types import Message, Chat


API_URL = "http://127.0.0.1:8000"

if "chat_id" not in st.session_state:
    st.session_state.chat_id = httpx.post(f"{API_URL}/chat").text[1:-1]

if "messages" not in st.session_state:
    st.session_state.messages = []

print(st.session_state.chat_id)
chat = httpx.get(f"{API_URL}/chat/{st.session_state.chat_id}").json()

st.session_state.messages = [
    {"role": message["role"], "content": message["content"]}
    for message in chat["history"]
]

st.title("Simple chat")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with httpx.stream(
            "POST",
            f"{API_URL}/message",
            json={
                "chat_id": st.session_state.chat_id,
                "message": {"role": "user", "content": prompt},
            },
        ) as response:
            answer = st.write_stream(response.iter_text())
    st.session_state.messages.append({"role": "assistant", "content": answer})
