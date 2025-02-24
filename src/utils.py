import streamlit as st
import openai
from typing import Dict, List, Optional, Any, Tuple
from pinecone import Pinecone, PineconeException
from .config import GPT_MODEL, MAX_TOKENS, TEMPERATURE
from .prompts import SYSTEM_PROMPT, get_chat_prompt

class APIError(Exception):
    """Custom exception for API related errors"""
    pass

def initialize_services() -> Optional[Any]:
    """
    Initialize Pinecone and OpenAI services.
    Returns:
        Pinecone Index object if successful, None otherwise
    """
    try:
        # Validate API keys
        if not st.secrets["PINECONE_API_KEY"] or not st.secrets["OPENAI_API_KEY"]:
            raise APIError("API keys not found in secrets")

        # Initialize services
        pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        index = pc.Index("amcbots")
        openai.api_key = st.secrets["OPENAI_API_KEY"]

        return index

    except APIError as e:
        st.error(f"API Configuration Error: {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"Service Initialization Error: {str(e)}")
        st.stop()
    return None

def get_query_embedding(query: str) -> List[float]:
    """
    Generate embeddings for the query using OpenAI's embedding model.

    Args:
        query: Input text to generate embeddings for

    Returns:
        List of floating point numbers representing the embedding
    """
    try:
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=query
        )
        return response['data'][0]['embedding']
    except openai.error.OpenAIError as e:
        st.error(f"OpenAI Embedding API error: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Unexpected error generating embeddings: {str(e)}")
        return []

def sanitize_query(query: str) -> str:
    """
    Sanitize and prepare the query string.

    Args:
        query: Raw input query

    Returns:
        Sanitized query string
    """
    # Remove extra whitespace and special characters
    query = " ".join(query.split())
    # Limit query length
    return query[:1000]

def process_pinecone_results(matches: List[Dict]) -> Tuple[str, List[str]]:
    """
    Process and extract relevant information from Pinecone matches.

    Args:
        matches: List of matching documents from Pinecone

    Returns:
        Tuple containing combined context string and list of references
    """
    context_parts = []
    references = []

    for match in matches:
        if match.metadata:
            # Extract text content
            text = match.metadata.get("text", "")
            if text:
                context_parts.append(text)

            # Extract reference information
            ref = match.metadata.get("reference", "")
            if ref:
                references.append(ref)

    return " ".join(context_parts), references

def query_pinecone(index: Any, namespace: str, query: str) -> List[Dict]:
    """
    Query Pinecone index for relevant context.

    Args:
        index: Pinecone index object
        namespace: Namespace to query
        query: User query string

    Returns:
        List of matching documents with metadata
    """
    try:
        # Sanitize query
        clean_query = sanitize_query(query)

        # Generate query embedding
        query_vector = get_query_embedding(clean_query)
        if not query_vector:
            return []

        # Query Pinecone
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

def generate_response(context: str, user_input: str, references: List[str] = None) -> str:
    """
    Generate response using OpenAI's GPT model.

    Args:
        context: Retrieved context from Pinecone
        user_input: Original user query
        references: List of reference documents

    Returns:
        Generated response in Gujarati
    """
    try:
        # Prepare messages with context and references
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": get_chat_prompt(context, user_input)}
        ]

        # Add references if available
        if references:
            ref_text = "\n\nReferences:\n" + "\n".join(references)
            messages[1]["content"] += ref_text

        # Generate response
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )

        return response.choices[0].message.content.strip()

    except openai.error.OpenAIError as e:
        error_msg = f"OpenAI API error: {str(e)}"
        st.error(error_msg)
        return "માફ કરશો, જવાબ જનરેટ કરવામાં ભૂલ આવી છે. કૃપા કરી થોડી વાર પછી ફરી પ્રયાસ કરો."
    except Exception as e:
        error_msg = f"Unexpected error generating response: {str(e)}"
        st.error(error_msg)
        return "માફ કરશો, સિસ્ટમમાં તકનીકી ખામી આવી છે. કૃપા કરી થોડી વાર પછી ફરી પ્રયાસ કરો."

def log_error(error: Exception, context: str) -> None:
    """
    Log errors for debugging purposes.

    Args:
        error: Exception object
        context: Context where the error occurred
    """
    # You can implement your preferred logging mechanism here
    st.error(f"Error in {context}: {str(error)}")
    # Could also log to file or monitoring service
    print(f"Error in {context}: {str(error)}")

def validate_response(response: str) -> bool:
    """
    Validate the generated response.

    Args:
        response: Generated response string

    Returns:
        Boolean indicating if response is valid
    """
    if not response:
        return False
    if len(response) < 10:  # Arbitrary minimum length
        return False
    # Add more validation as needed
    return True

def process_user_query(index: Any, query: str, namespace: str) -> Tuple[str, bool]:
    """
    Process user query end-to-end.

    Args:
        index: Pinecone index object
        query: User query string
        namespace: Namespace to query

    Returns:
        Tuple containing response string and success boolean
    """
    try:
        # Get relevant documents
        matches = query_pinecone(index, namespace, query)
        if not matches:
            return "માફ કરશો, કોई સંબંધિત માહિતી મળી નથી.", False

        # Process results
        context, references = process_pinecone_results(matches)

        # Generate response
        response = generate_response(context, query, references)

        # Validate response
        if not validate_response(response):
            return "માફ કરશો, યોગ્ય જવાબ જનરેટ કરવામાં અસમર્થ છું.", False

        return response, True

    except Exception as e:
        log_error(e, "process_user_query")
        return "માફ કરશો, પ્રક્રિયા દરમિયાન ભૂલ આવી છે.", False
