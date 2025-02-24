import streamlit as st
from typing import Dict, List
from pinecone import Pinecone, PineconeException
import openai
from .config import GPT_MODEL, MAX_TOKENS, TEMPERATURE
from .prompts import SYSTEM_PROMPT, get_chat_prompt

def initialize_services():
    """Initialize Pinecone and OpenAI services"""
    try:
        pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        index = pc.Index("amcbots")
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        return index
    except Exception as e:
        st.error(f"Error initializing services: {str(e)}")
        st.stop()
        return None

def query_pinecone(index, namespace: str, query: str) -> List[Dict]:
    """Query Pinecone index for relevant context"""
    try:
        response = index.query(
            namespace=namespace,
            top_k=5,
            include_metadata=True,
            vector=query
        )
        return response['matches']
    except PineconeException as e:
        st.error(f"Pinecone query error: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Unexpected error during query: {str(e)}")
        return []

def generate_response(context: str, user_input: str) -> str:
    """Generate response using OpenAI"""
    try:
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": get_chat_prompt(context, user_input)}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        return response.choices[0].message.content.strip()
    except openai.error.OpenAIError as e:
        st.error(f"OpenAI API error: {str(e)}")
        return "માફ કરશો, જવાબ જનરેટ કરવામાં ભૂલ આવી છે. કૃપા કરી થોડી વાર પછી ફરી પ્રયાસ કરો."
    except Exception as e:
        st.error(f"Unexpected error generating response: {str(e)}")
        return "માફ કરશો, સિસ્ટમમાં તકનીકી ખામી આવી છે. કૃપા કરી થોડી વાર પછી ફરી પ્રયાસ કરો."
