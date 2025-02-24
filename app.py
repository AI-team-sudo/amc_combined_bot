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
        .main-header {
            font-size: 2.5rem;
            color: #1E3A8A;
            text-align: center;
            margin-bottom: 2rem;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #1E3A8A;
            margin-bottom: 1rem;
        }
        .stRadio > div {
            padding: 10px;
            background-color: #f0f2f6;
            border-radius: 5px;
        }
        .chat-message {
            padding: 1.5rem;
            border-radius: 0.5rem;
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
            position: absolute;
            top: 0.5rem;
            left: 0.5rem;
            font-size: 0.8rem;
            color: #666;
        }
        .error-message {
            color: #d32f2f;
            background-color: #ffebee;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .info-box {
            background-color: #e3f2fd;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .loading-spinner {
            text-align: center;
            padding: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = list(NAMESPACE_MAP.keys())[0]

def display_sidebar():
    """Display and configure sidebar elements"""
    with st.sidebar:
        try:
            st.image(AMC_LOGO_URL, width=150)
        except Exception:
            st.error("Error loading AMC logo")

        st.markdown("### Ahmedabad Municipal Corporation")
        st.markdown("**અમદાવાદ મ્યુનિસિપલ કોર્પોરેશન**")
        st.markdown("---")

        st.markdown("### Available Topics")
        for topic in NAMESPACE_MAP.keys():
            st.markdown(f"- {topic}")

        st.markdown("---")
        st.markdown("### Instructions")
        st.markdown("""
        1. Select a topic from the main page
        2. Type your question in English or Gujarati
        3. Responses will always be in Gujarati
        4. Be specific in your questions
        """)

        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.success("Chat history cleared!")

def display_chat_messages():
    """Display chat message history"""
    for idx, message in enumerate(st.session_state.messages):
        # User message
        with st.container():
            st.markdown(
                f"""<div class="chat-message user-message">
                    <div class="message-label">You</div>
                    <div style="margin-top: 1rem">{message["user"]}</div>
                </div>""",
                unsafe_allow_html=True
            )

        # Bot message
        with st.container():
            st.markdown(
                f"""<div class="chat-message bot-message">
                    <div class="message-label">Bot</div>
                    <div style="margin-top: 1rem">{message["bot"]}</div>
                </div>""",
                unsafe_allow_html=True
            )

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

    # Display sidebar
    display_sidebar()

    # Main content
    st.markdown('<h1 class="main-header">AMC Information Chatbot</h1>', unsafe_allow_html=True)

    # Topic selection
    st.markdown('<h2 class="sub-header">Select Topic</h2>', unsafe_allow_html=True)
    topic = st.radio(
        "Choose a topic to query:",
        tuple(NAMESPACE_MAP.keys()),
        key="topic_selector"
    )

    # Update current topic in session state
    st.session_state.current_topic = topic
    namespace = NAMESPACE_MAP[topic]

    # Display current topic info
    st.markdown(
        f"""<div class="info-box">
            Currently selected topic: <strong>{topic}</strong>
        </div>""",
        unsafe_allow_html=True
    )

    # User input
    user_input = st.text_input(
        "Enter your question (English or Gujarati):",
        key="user_input",
        placeholder="Type your question here..."
    )

    # Process user input
    if user_input:
        with st.spinner("Processing your query..."):
            try:
                response, success = process_user_query(index, openai_client, user_input, namespace)

                if success:
                    st.session_state.messages.append({
                        "user": user_input,
                        "bot": response
                    })
                else:
                    st.error("Failed to get a valid response. Please try again.")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.markdown(
                    """<div class="error-message">
                        Please try again later or contact support if the problem persists.
                    </div>""",
                    unsafe_allow_html=True
                )

    # Display chat history
    if st.session_state.messages:
        st.markdown('<h2 class="sub-header">Chat History</h2>', unsafe_allow_html=True)
        display_chat_messages()
    else:
        st.markdown(
            """<div class="info-box">
                No messages yet. Start by asking a question above!
            </div>""",
            unsafe_allow_html=True
        )

    # Footer
    st.markdown("---")
    st.markdown(
        """<div style="text-align: center; color: #666;">
            Powered by Ahmedabad Municipal Corporation
        </div>""",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
