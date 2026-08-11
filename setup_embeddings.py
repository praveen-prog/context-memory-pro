from db_connection import get_connection
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_embedding_groq(text):
    # Use Groq's embedding endpoint
    response = requests.post(
        "https://api.groq.com/openai/v1/embeddings",
        headers={
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-8b-8192",
            "input": text
        },
        timeout=10
    )
    result = response.json()
    print(result)
    return result

# Test first
result = get_embedding_groq("Buy milk")
print(result)