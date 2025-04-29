import streamlit as st
import requests
import uuid
from datetime import datetime

# Constants
API_URL = "http://127.0.0.1:8000"

# Initialize session state
if "chat_id" not in st.session_state:
    # Get a new chat ID from the backend
    response = requests.post(f"{API_URL}/create_chat")
    st.session_state.chat_id = response.json()["chat_id"]
    st.session_state.messages = []

# App title
st.title("Chat Agent Memory Demo")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Save user message to backend
    requests.post(
        f"{API_URL}/save_message",
        json={
            "chat_id": st.session_state.chat_id,
            "role": "user",
            "content": prompt
        }
    )
    
    # Get assistant response (echo in this simple case)
    with st.chat_message("assistant"):
        response = requests.post(
            f"{API_URL}/save_message",
            json={
                "chat_id": st.session_state.chat_id,
                "role": "assistant",
                "content": f"Echo: {prompt}"
            }
        ).json()
        
        st.write(response["content"])
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response["content"]})

# Show chat information in sidebar
with st.sidebar:
    st.subheader("Chat Information")
    st.write(f"Chat ID: {st.session_state.chat_id}")
    
    if st.button("Refresh Chat"):
        # Fetch latest messages from backend
        response = requests.get(f"{API_URL}/get_chat/{st.session_state.chat_id}")
        messages = response.json()["messages"]
        st.session_state.messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
        st.rerun() 