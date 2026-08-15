from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from db_connection import get_connection
from datetime import datetime, timezone

router = APIRouter()

class TaskAdd(BaseModel):
    user_id: str
    location_id: str
    title: str
    description: Optional[str] = ""
    priority: int = 1

class TaskComplete(BaseModel):
    task_id: str
    user_id: str
    method: str = "manual"

@router.post("/add")
def add_task(payload: TaskAdd):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tasks (user_id, location_id, title, description, status, priority)
        VALUES (%s, %s, %s, %s, 'pending', %s)
        RETURNING id, title, status
    """, (payload.user_id, payload.location_id, payload.title, payload.description, payload.priority))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    return {"status": "added", "task": {"id": str(row[0]), "title": row[1], "status": row[2]}}

@router.post("/complete")
def complete_task(payload: TaskComplete):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE tasks SET status = 'completed', completed_at = %s
        WHERE id = %s AND user_id = %s RETURNING title
    """, (datetime.now(timezone.utc), payload.task_id, payload.user_id))
    row = cur.fetchone()
    if row:
        cur.execute("""
            INSERT INTO task_completions (task_id, user_id, method, confidence)
            VALUES (%s, %s, %s, %s)
        """, (payload.task_id, payload.user_id, payload.method, 1.0))
    conn.commit()
    conn.close()
    return {"status": "completed", "task": row[0] if row else None}

@router.get("/{user_id}/{location_id}")
def get_tasks(user_id: str, location_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, description, status, priority FROM tasks
        WHERE user_id = %s AND location_id = %s
        ORDER BY priority DESC
    """, (user_id, location_id))
    rows = cur.fetchall()
    conn.close()
    return {"tasks": [{"id": str(r[0]), "title": r[1], "description": r[2], "status": r[3], "priority": r[4]} for r in rows]}

class TaskUpdate(BaseModel):
    task_id: str
    user_id: str
    title: str

@router.put("/update")
def update_task(payload: TaskUpdate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET title = %s WHERE id = %s AND user_id = %s RETURNING title",
                (payload.title, payload.task_id, payload.user_id))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    return {"status": "updated", "title": row[0] if row else None}

class TaskDelete(BaseModel):
    task_id: str
    user_id: str

@router.delete("/delete")
def delete_task(payload: TaskDelete):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM nudge_events WHERE task_id = %s", (payload.task_id,))
    cur.execute("DELETE FROM task_completions WHERE task_id = %s", (payload.task_id,))
    cur.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s RETURNING title",
                (payload.task_id, payload.user_id))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    return {"status": "deleted", "task": row[0] if row else None}
