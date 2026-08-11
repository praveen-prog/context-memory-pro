from dotenv import load_dotenv
import os, requests
load_dotenv()
r = requests.get('https://api.groq.com/openai/v1/models', 
    headers={'Authorization': 'Bearer ' + os.getenv('GROQ_API_KEY')})
print(r.status_code)
data = r.json()
if 'data' in data:
    print([m['id'] for m in data['data']])
else:
    print(data)