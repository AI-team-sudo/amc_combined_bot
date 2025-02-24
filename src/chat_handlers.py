import streamlit as st
from .utils import query_pinecone, generate_response
from .config import NAMESPACE_MAP

def handle_user_input(index, user_input: str, namespace: str):
    """Handle user input and generate response"""
    if user_input:
        matches = query_pinecone(index, namespace, user_input)
        if matches:
            context = " ".join([item.metadata.get("text", "") for item in matches])
            bot_response = generate_response(context, user_input)
            st.session_state.messages.append({"user": user_input, "bot": bot_response})

def display_chat_history():
    """Display chat history"""
    for message in st.session_state.messages:
        st.markdown(f"**You:** {message['user']}")
        st.markdown(f"**Bot:** {message['bot']}")
