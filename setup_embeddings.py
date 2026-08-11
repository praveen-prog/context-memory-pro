from db_connection import get_connection
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import os, time

load_dotenv()

client = InferenceClient(token=os.getenv('HUGGINGFACE_API_TOKEN'))
MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

def get_embedding(text):
    try:
        result = client.feature_extraction(text, model=MODEL)
        return result.tolist() if hasattr(result, 'tolist') else list(result)
    except Exception as e:
        print(f"Error: {e}")
        return None

print("Testing HuggingFace...")
test = get_embedding("Buy milk")
if test:
    print(f"OK — dims: {len(test)}")
else:
    print("FAILED"); exit()

conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT id, title FROM tasks WHERE embedding IS NULL")
tasks = cur.fetchall()
print(f"Tasks to embed: {len(tasks)}")

for task_id, title in tasks:
    print(f"  Embedding: {title}")
    embedding = get_embedding(title)
    if embedding:
        embedding_str = '[' + ','.join([str(x) for x in embedding]) + ']'
        cur.execute("UPDATE tasks SET embedding = %s::vector WHERE id = %s",
                   (embedding_str, str(task_id)))
        conn.commit()
        print(f"  Done ✓")
    time.sleep(0.3)

cur.execute("SELECT COUNT(*) FROM tasks WHERE embedding IS NOT NULL")
print(f"\nEmbedded: {cur.fetchone()[0]} tasks")
conn.close()
print("All done!")
