from dotenv import load_dotenv
import os, requests
load_dotenv()

token = os.getenv('HUGGINGFACE_API_TOKEN')

# Try different HuggingFace endpoints
urls = [
    'https://huggingface.co',
    'https://router.huggingface.co',
    'https://huggingface.co/api/models/sentence-transformers/all-MiniLM-L6-v2',
]

for url in urls:
    try:
        r = requests.get(url, timeout=5)
        print(f"OK {r.status_code}: {url}")
    except Exception as e:
        print(f"FAIL: {url} — {e}")