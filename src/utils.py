import streamlit as st
import openai
from openai import OpenAI
from typing import Dict, List, Optional, Any, Tuple
from pinecone import Pinecone, PineconeException

from .config import GPT_MODEL, MAX_TOKENS, TEMPERATURE, NAMESPACE_MAP
from .prompts import SYSTEM_PROMPT, get_chat_prompt

class APIError(Exception):
    """Custom exception for API related errors"""
    pass

def initialize_services() -> Tuple[Any, OpenAI]:
    """
    Initialize Pinecone and OpenAI services.
    Returns:
        Tuple of (Pinecone Index object, OpenAI client) if successful
    """
    try:
        # Validate API keys
        if not st.secrets["PINECONE_API_KEY"] or not st.secrets["OPENAI_API_KEY"]:
            raise APIError("API keys not found in secrets")

        # Initialize services
        pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        index = pc.Index("amcbots")

        # Initialize OpenAI client
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        return index, client

    except APIError as e:
        st.error(f"API Configuration Error: {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"Service Initialization Error: {str(e)}")
        st.stop()

def get_query_embedding(client: OpenAI, query: str) -> List[float]:
    """
    Generate embeddings for the query using OpenAI's embedding model.

    Args:
        client: OpenAI client instance
        query: Input text to generate embeddings for

    Returns:
        List of floating point numbers representing the embedding
    """
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=query
        )
        return response.data[0].embedding
    except Exception as e:
        st.error(f"OpenAI Embedding API error: {str(e)}")
        return []

def sanitize_query(query: str) -> str:
    """
    Sanitize and prepare the query string.
    """
    query = " ".join(query.split())
    return query[:1000]

def process_pinecone_results(matches: List[Dict]) -> Tuple[str, List[str]]:
    """
    Process and extract relevant information from Pinecone matches.
    """
    context_parts = []
    references = []

    for match in matches:
        if match.metadata:
            text = match.metadata.get("text", "")
            if text:
                context_parts.append(text)

            ref = match.metadata.get("reference", "")
            if ref:
                references.append(ref)

    return " ".join(context_parts), references

def query_pinecone(index: Any, client: OpenAI, namespace: str, query: str) -> List[Dict]:
    """
    Query Pinecone index for relevant context.

    Args:
        index: Pinecone index object
        client: OpenAI client instance
        namespace: Namespace to query
        query: User query string
    """
    try:
        clean_query = sanitize_query(query)
        query_vector = get_query_embedding(client, clean_query)

        if not query_vector:
            return []

        response = index.query(
            vector=query_vector,
            namespace=namespace,
            top_k=5,
            include_metadata=True
        )

        return response['matches']

    except PineconeException as e:
        st.error(f"Pinecone query error: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Unexpected error during query: {str(e)}")
        return []

def generate_response(client: OpenAI, context: str, user_input: str, references: List[str] = None) -> str:
    """
    Generate response using OpenAI's GPT model.

    Args:
        client: OpenAI client instance
        context: Retrieved context from Pinecone
        user_input: Original user query
        references: List of reference documents
    """
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": get_chat_prompt(context, user_input)}
        ]

        if references:
            ref_text = "\n\nReferences:\n" + "\n".join(references)
            messages[1]["content"] += ref_text

        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        st.error(f"OpenAI API error: {str(e)}")
        return "માફ કરશો, જવાબ જનરેટ કરવામાં ભૂલ આવી છે. કૃપા કરી થોડી વાર પછી ફરી પ્રયાસ કરો."

def log_error(error: Exception, context: str) -> None:
    """Log errors for debugging purposes."""
    st.error(f"Error in {context}: {str(error)}")
    print(f"Error in {context}: {str(error)}")

def validate_response(response: str) -> bool:
    """Validate the generated response."""
    if not response:
        return False
    if len(response) < 10:
        return False
    return True
def process_user_query(index: Any, client: OpenAI, query: str, namespace: str = None) -> Tuple[str, bool]:
    """
    Process user query across all namespaces or specific namespace.

    Args:
        index: Pinecone index object
        client: OpenAI client instance
        query: User query string
        namespace: Optional namespace to query (if None, queries all namespaces)
    """
    try:
        all_matches = []

        if namespace:
            # Query specific namespace
            matches = query_pinecone(index, client, namespace, query)
            all_matches.extend(matches)
        else:
            # Query all namespaces
            for ns in NAMESPACE_MAP.values():
                matches = query_pinecone(index, client, ns, query)
                if matches:
                    all_matches.extend(matches)

        # Sort matches by score and take top 5
        all_matches.sort(key=lambda x: x.score, reverse=True)
        top_matches = all_matches[:5]

        if not top_matches:
            return "માફ કરશો, કોई સંબંધિત માહિતી મળી નથી.", False

        # Process results
        context, references = process_pinecone_results(top_matches)

        # Generate response
        response = generate_response(client, context, query, references)

        if not validate_response(response):
            return "માફ કરશો, યોગ્ય જવાબ જનરેટ કરવામાં અસમર્થ છું.", False

        return response, True

    except Exception as e:
        log_error(e, "process_user_query")
        return "માફ કરશો, પ્રક્રિયા દરમિયાન ભૂલ આવી છે.", False
