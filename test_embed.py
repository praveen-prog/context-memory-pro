from dotenv import load_dotenv
import os, requests
load_dotenv()

r = requests.post(
    'https://api.groq.com/openai/v1/embeddings',
    headers={
        'Authorization': 'Bearer ' + os.getenv('GROQ_API_KEY'),
        'Content-Type': 'application/json'
    },
    json={
        'model': 'llama-3.1-8b-instant',
        'input': 'Buy milk'
    }
)
print(r.status_code)
print(r.json())