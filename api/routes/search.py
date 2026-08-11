from fastapi import APIRouter
from pydantic import BaseModel
from db_connection import get_connection
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

load_dotenv()
router = APIRouter()

def get_embedding(text: str):
    try:
        client = InferenceClient(token=os.getenv('HUGGINGFACE_API_TOKEN'))
        result = client.feature_extraction(text, model='sentence-transformers/all-MiniLM-L6-v2')
        return result.tolist() if hasattr(result, 'tolist') else list(result)
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

class SearchRequest(BaseModel):
    user_id: str
    query: str
    limit: int = 5

@router.post("/similar")
def search_similar_tasks(payload: SearchRequest):
    embedding = get_embedding(payload.query)
    conn = get_connection()
    cur = conn.cursor()

    if embedding:
        embedding_str = '[' + ','.join([str(x) for x in embedding]) + ']'
        cur.execute("""
            SELECT t.id, t.title, t.status, l.name,
                   t.embedding <-> %s::vector AS distance
            FROM tasks t
            JOIN locations l ON t.location_id = l.id
            WHERE t.user_id = %s AND t.embedding IS NOT NULL
            ORDER BY t.embedding <-> %s::vector
            LIMIT %s
        """, (embedding_str, payload.user_id, embedding_str, payload.limit))
        rows = cur.fetchall()
        conn.close()
        return {
            "query": payload.query,
            "mode": "vector",
            "results": [{"id": str(r[0]), "title": r[1], "status": r[2], "location": r[3], "similarity": round(1-float(r[4]),3)} for r in rows]
        }
    else:
        cur.execute("""
            SELECT t.id, t.title, t.status, l.name
            FROM tasks t JOIN locations l ON t.location_id = l.id
            WHERE t.user_id = %s AND LOWER(t.title) LIKE %s
            LIMIT %s
        """, (payload.user_id, '%'+payload.query.lower()+'%', payload.limit))
        rows = cur.fetchall()
        conn.close()
        return {
            "query": payload.query,
            "mode": "keyword",
            "results": [{"id": str(r[0]), "title": r[1], "status": r[2], "location": r[3]} for r in rows]
        }

@router.get("/history/{user_id}")
def nudge_history(user_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT n.trigger_type, n.message, n.created_at,
               t.title, l.name as location
        FROM nudge_events n
        JOIN tasks t ON n.task_id = t.id
        JOIN locations l ON t.location_id = l.id
        WHERE n.user_id = %s
        ORDER BY n.created_at DESC
        LIMIT 20
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return {"history": [{"trigger": r[0], "message": r[1], "time": str(r[2]), "task": r[3], "location": r[4]} for r in rows]}