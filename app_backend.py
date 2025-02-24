from fastapi import FastAPI, Request
from pydantic import BaseModel
from pinecone import Index
import openai

# Initialize FastAPI app
app = FastAPI()

# Initialize Pinecone
import pinecone
pinecone.init(api_key="YOUR_PINECONE_API_KEY", environment="YOUR_PINECONE_ENV")
index = pinecone.Index("amcbots")

# OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Define request model
class QueryRequest(BaseModel):
    user_input: str
    namespace: str

# Translate text to Gujarati
def translate_to_gujarati(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Translate the following text to Gujarati."},
            {"role": "user", "content": text}
        ]
    )
    return response['choices'][0]['message']['content']

# Query Pinecone and generate response
@app.post("/query")
async def query_pinecone(request: QueryRequest):
    user_input = request.user_input
    namespace = request.namespace

    # Translate input to Gujarati if needed
    translated_input = translate_to_gujarati(user_input)

    # Query Pinecone
    query_response = index.query(
        vector=translated_input,  # Use embeddings for better results
        namespace=namespace,
        top_k=3,
        include_metadata=True
    )

    # Extract relevant information
    results = [match['metadata']['text'] for match in query_response['matches']]

    # Generate response in Gujarati
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Answer the following query in Gujarati."},
            {"role": "user", "content": f"Query: {translated_input}\nResults: {results}"}
        ]
    )
    return {"response": response['choices'][0]['message']['content']}
