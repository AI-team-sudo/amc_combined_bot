import streamlit as st
from src.utils import initialize_services
from src.chat_handlers import handle_user_input, display_chat_history
from src.config import (
    PAGE_TITLE,
    PAGE_ICON,
    AMC_LOGO_URL,
    NAMESPACE_MAP
)

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide"
)

# Load custom CSS
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize services
index = initialize_services()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    try:
        st.image(AMC_LOGO_URL, width=150)
    except Exception:
        st.error("Error loading AMC logo")

    st.markdown("### Ahmedabad Municipal Corporation")
    st.markdown("**અમદાવાદ મ્યુનિસિપલ કોર્પોરેશન**")
    st.markdown("---")
    st.markdown("This chatbot provides information on:")
    st.markdown("- GPMC Act (English)")
    st.markdown("- Compilation of Circulars (Gujarati)")
    st.markdown("- Tax Laws (Gujarati)")
    st.markdown("---")
    st.markdown("**Instructions:**")
    st.markdown("1. Select a topic to search for.")
    st.markdown("2. Enter your query in English or Gujarati.")
    st.markdown("3. The response will always be in Gujarati.")

# Main content
st.title("AMC Chatbot")
st.markdown("**Welcome to the Ahmedabad Municipal Corporation Chatbot!**")
st.markdown("Please select a topic to begin:")

# Topic selection
topic = st.radio(
    "Choose a topic:",
    tuple(NAMESPACE_MAP.keys())
)

namespace = NAMESPACE_MAP[topic]

# Chat interface
user_input = st.text_input("Enter your query (in English or Gujarati):")

# Handle user input and display chat
handle_user_input(index, user_input, namespace)
display_chat_history()
