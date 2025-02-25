import streamlit as st
import time
from src.utils import initialize_services, process_user_query
from src.config import (
    PAGE_TITLE,
    PAGE_ICON,
    AMC_LOGO_URL,
    NAMESPACE_MAP
)

def load_css():
    """Load custom CSS styles"""
    st.markdown("""
        <style>
        .contact-list {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 5px;
            height: 100%;
            overflow-y: auto;
        }
        .contact-item {
            padding: 0.8rem;
            margin-bottom: 0.5rem;
            border-radius: 5px;
            cursor: pointer;
            display: flex;
            align-items: center;
            background-color: #ffffff;
            border: 1px solid #ddd;
        }
        .contact-item:hover {
            background-color: #e3f2fd;
        }
        .contact-item.active {
            background-color: #bbdefb;
            border-left: 5px solid #1976d2;
        }
        .chat-container {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 5px;
            height: 100%;
            overflow-y: auto;
        }
        .chat-message {
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
            position: relative;
        }
        .user-message {
            background-color: #e3f2fd;
            border-left: 5px solid #1976d2;
        }
        .bot-message {
            background-color: #f5f5f5;
            border-left: 5px solid #4caf50;
        }
        .message-label {
            font-size: 0.8rem;
            color: #666;
        }
        .input-container {
            margin-top: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = {namespace: [] for namespace in NAMESPACE_MAP.keys()}
    if "current_namespace" not in st.session_state:
        st.session_state.current_namespace = list(NAMESPACE_MAP.keys())[0]

def display_contact_list():
    """Display the list of namespaces as contacts"""
    st.markdown('<div class="contact-list">', unsafe_allow_html=True)
    for namespace in NAMESPACE_MAP.keys():
        active_class = "active" if namespace == st.session_state.current_namespace else ""
        if st.button(namespace, key=f"contact_{namespace}"):
            st.session_state.current_namespace = namespace
        st.markdown(
            f"""<div class="contact-item {active_class}">
                <strong>{namespace}</strong>
            </div>""",
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

def display_chat_messages():
    """Display chat messages for the selected namespace"""
    namespace = st.session_state.current_namespace
    messages = st.session_state.messages[namespace]

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in messages:
        # User message
        st.markdown(
            f"""<div class="chat-message user-message">
                <div class="message-label">You</div>
                <div>{message["user"]}</div>
            </div>""",
            unsafe_allow_html=True
        )
        # Bot message
        st.markdown(
            f"""<div class="chat-message bot-message">
                <div class="message-label">Bot</div>
                <div>{message["bot"]}</div>
            </div>""",
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Load custom CSS
    load_css()

    # Initialize session state
    initialize_session_state()

    try:
        # Initialize services
        index, openai_client = initialize_services()
    except Exception as e:
        st.error(f"Failed to initialize services: {str(e)}")
        st.stop()

    # Layout: Two columns
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("### Contacts")
        display_contact_list()

    with col2:
        st.markdown(f"### Chat with {st.session_state.current_namespace}")
        display_chat_messages()

        # User input
        user_input = st.text_input(
            "Enter your question:",
            key="user_input",
            placeholder="Type your question here..."
        )

        if user_input:
            with st.spinner("Processing your query..."):
                try:
                    namespace = NAMESPACE_MAP[st.session_state.current_namespace]
                    response, success = process_user_query(index, openai_client, user_input, namespace)

                    if success:
                        st.session_state.messages[st.session_state.current_namespace].append({
                            "user": user_input,
                            "bot": response
                        })
                    else:
                        st.error("Failed to get a valid response. Please try again.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
