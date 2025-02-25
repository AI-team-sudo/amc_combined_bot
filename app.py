import streamlit as st
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
            text-align: left;
            color: #1976d2;
            padding: 1rem 0;
            margin-bottom: 2rem;
            border-bottom: 2px solid #e0e0e0;
            font-size: 2rem;
            line-height: 1.4;
            font-weight: 600;
        }
        .sidebar-logo {
            text-align: center;
            margin: 1rem 0;
            padding: 1rem;
            border-bottom: 1px solid #e0e0e0;
        }
        .sidebar-logo img {
            max-width: 120px;
            margin-bottom: 1rem;
        }
        .contact-list {
            background-color: #f8f9fa;
            padding: 1.2rem;
            border-radius: 8px;
            height: 100%;
            overflow-y: auto;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .contact-item {
            padding: 1rem;
            margin-bottom: 0.8rem;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            transition: all 0.3s ease;
        }
        .contact-item:hover {
            background-color: #e8f0fe;
            transform: translateY(-2px);
        }
        .contact-item.active {
            background-color: #e3f2fd;
            border-left: 5px solid #1976d2;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .chat-container {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 8px;
            height: calc(100vh - 400px);
            overflow-y: auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-top: 1rem;
        }
        .chat-message {
            padding: 1.2rem;
            border-radius: 8px;
            margin-bottom: 1.2rem;
            position: relative;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
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
            font-size: 0.9rem;
            color: #555;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        .input-container {
            margin-top: 1.5rem;
            padding: 1rem;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .stTextInput input {
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            padding: 0.8rem;
        }
        .stTextInput input:focus {
            border-color: #1976d2;
            box-shadow: 0 0 0 2px rgba(25,118,210,0.1);
        }
        .subheader {
            color: #1976d2;
            font-size: 1.5rem;
            margin-top: 1rem;
            margin-bottom: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = {namespace: [] for namespace in NAMESPACE_MAP.keys()}
    if "current_namespace" not in st.session_state:
        st.session_state.current_namespace = list(NAMESPACE_MAP.keys())[0]

def display_sidebar():
    """Display the sidebar with the AMC logo and contact list"""
    st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    st.image(AMC_LOGO_URL, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="contact-list">', unsafe_allow_html=True)
    for namespace in NAMESPACE_MAP.keys():
        active_class = "active" if namespace == st.session_state.current_namespace else ""
        if st.button(namespace, key=f"contact_{namespace}"):
            st.session_state.current_namespace = namespace
    st.markdown('</div>', unsafe_allow_html=True)

def display_chat_messages():
    """Display chat messages for the selected namespace"""
    namespace = st.session_state.current_namespace
    messages = st.session_state.messages[namespace]

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    if not messages:
        st.markdown(
            '<div class="chat-message bot-message">'
            '<div class="message-label">Bot</div>'
            '<div>Hello! How can I help you today?</div>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
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
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )

    load_css()
    initialize_session_state()

    try:
        index, openai_client = initialize_services()
    except Exception as e:
        st.error(f"Failed to initialize services: {str(e)}")
        st.stop()

    col1, col2 = st.columns([1, 3])

    with col1:
        display_sidebar()

    with col2:
        # Main header moved to right column
        st.markdown('<h1 class="main-header">AI Agents for the Ahmedabad Municipal Corporation</h1>', unsafe_allow_html=True)

        # Subheader for current namespace
        st.markdown(f'<div class="subheader">Know more about {st.session_state.current_namespace}</div>', unsafe_allow_html=True)

        display_chat_messages()

        # User input in a container
        with st.container():
            st.markdown('<div class="input-container">', unsafe_allow_html=True)
            user_input = st.text_input(
                "Enter your question:",
                key="user_input",
                placeholder="Type your question here..."
            )
            st.markdown('</div>', unsafe_allow_html=True)

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
