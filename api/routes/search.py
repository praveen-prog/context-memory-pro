from fastapi import APIRouter
from pydantic import BaseModel
from db_connection import get_connection

router = APIRouter()

class SearchRequest(BaseModel):
    user_id: str
    query: str
    limit: int = 5

@router.post("/similar")
def search_similar_tasks(payload: SearchRequest):
    conn = get_connection()
    cur = conn.cursor()

    # Check if any embeddings exist
    cur.execute("""
        SELECT COUNT(*) FROM tasks 
        WHERE user_id = %s AND embedding IS NOT NULL
    """, (payload.user_id,))
    count = cur.fetchone()[0]

    if count == 0:
        # Fallback to keyword search if no embeddings
        cur.execute("""
            SELECT t.id, t.title, t.status, l.name as location
            FROM tasks t
            JOIN locations l ON t.location_id = l.id
            WHERE t.user_id = %s
            AND LOWER(t.title) LIKE %s
            LIMIT %s
        """, (payload.user_id, '%' + payload.query.lower() + '%', payload.limit))
        rows = cur.fetchall()
        conn.close()
        return {
            "query": payload.query,
            "mode": "keyword",
            "results": [{"id": str(r[0]), "title": r[1], "status": r[2], "location": r[3]} for r in rows]
        }

    # Vector search using CockroachDB pgvector
    cur.execute("""
        SELECT t.id, t.title, t.status, l.name as location,
               t.embedding <-> (
                   SELECT embedding FROM tasks 
                   WHERE user_id = %s AND embedding IS NOT NULL
                   AND LOWER(title) LIKE %s
                   LIMIT 1
               ) AS distance
        FROM tasks t
        JOIN locations l ON t.location_id = l.id
        WHERE t.user_id = %s
          AND t.embedding IS NOT NULL
        ORDER BY distance
        LIMIT %s
    """, (payload.user_id, '%' + payload.query.lower() + '%',
          payload.user_id, payload.limit))
    rows = cur.fetchall()
    conn.close()

    return {
        "query": payload.query,
        "mode": "vector",
        "results": [
            {
                "id": str(r[0]),
                "title": r[1],
                "status": r[2],
                "location": r[3],
                "similarity": round(1 - float(r[4]), 3) if r[4] else None
            }
            for r in rows
        ]
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
    return {
        "history": [
            {
                "trigger": r[0],
                "message": r[1],
                "time": str(r[2]),
                "task": r[3],
                "location": r[4]
            }
            for r in rows
        ]
    }