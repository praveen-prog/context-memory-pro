from dotenv import load_dotenv
import os, requests
load_dotenv()

token = os.getenv('HUGGINGFACE_API_TOKEN')

r = requests.post(
    'https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2',
    headers={'Authorization': 'Bearer ' + token},
    json={'inputs': 'Buy milk'},
    verify=False,
    timeout=15
)
print(r.status_code)
print(type(r.json()))
print(len(r.json()))