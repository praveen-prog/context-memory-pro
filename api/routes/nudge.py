from fastapi import APIRouter
from pydantic import BaseModel
from db_connection import get_connection
import os
import random
import requests
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

def generate_nudge_groq(trigger_type: str, tasks: list, location_name: str, elder_mode: bool = False) -> str:
    count = len(tasks)
    first = tasks[0]["title"] if tasks else "your items"
    task_list = ", ".join([t["title"] for t in tasks[:3]])
    if elder_mode:
        prompt = f"""Generate ONE gentle warm reminder (max 15 words).
Speak like a caring family member. No urgency. No warnings. No exclamation marks.
Use soft words like "just a reminder", "when you get a chance", "no rush".
Add one warm emoji like 🌸 😊 🌤
Trigger: {trigger_type}
Location: {location_name}
Items: {task_list}
Just the message, nothing else."""
    else:
        prompt = f"""Generate ONE short friendly reminder (max 15 words).
Trigger: {trigger_type}
Location: {location_name}
Items: {task_list}
Just the message, nothing else."""
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 50,
                "temperature": 0.7
            },
            timeout=10
        )
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception:
        return generate_nudge_fallback(trigger_type, tasks, location_name)

def generate_nudge_fallback(trigger_type: str, tasks: list, location_name: str) -> str:
    count = len(tasks)
    first = tasks[0]["title"] if tasks else "your items"
    others = count - 1
    templates = {
        "arrival": [
            f"You have {count} item{'s' if count > 1 else ''} to pick up here.",
            f"Don't forget {first}{f' and {others} more' if others > 0 else ''}.",
        ],
        "dwell": [
            f"Still need {first}? You've been here a while.",
            f"Don't leave without {first}.",
        ],
        "exit": [
            f"Wait — {first} is still unchecked!",
            f"Leaving without {first}?",
        ]
    }
    return random.choice(templates.get(trigger_type, [f"Don't forget {first}!"]))

class NudgeRequest(BaseModel):
    user_id: str
    location_id: str
    trigger_type: str
    elder_mode: bool = False

@router.post("/generate")
def generate_nudge_endpoint(payload: NudgeRequest):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT t.id, t.title, l.name FROM tasks t
        JOIN locations l ON t.location_id = l.id
        WHERE t.user_id = %s AND t.location_id = %s AND t.status = 'pending'
    """, (payload.user_id, payload.location_id))
    rows = cur.fetchall()
    if not rows:
        conn.close()
        return {"message": "All tasks completed!", "nudge": None}
    location_name = rows[0][2]
    tasks = [{"id": str(r[0]), "title": r[1]} for r in rows]
    message = generate_nudge_groq(payload.trigger_type, tasks, location_name, payload.elder_mode)
    cur.execute("""
        INSERT INTO nudge_events (user_id, task_id, trigger_type, message, delivered)
        VALUES (%s, %s, %s, %s, true)
    """, (payload.user_id, tasks[0]["id"], payload.trigger_type, message))
    conn.commit()
    conn.close()
    return {"nudge": message, "trigger_type": payload.trigger_type, "pending_tasks": tasks, "location": location_name}

@router.get("/history/{user_id}")
def nudge_history(user_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT n.trigger_type, n.message, n.created_at, t.title
        FROM nudge_events n JOIN tasks t ON n.task_id = t.id
        WHERE n.user_id = %s ORDER BY n.created_at DESC LIMIT 20
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return {"history": [{"trigger": r[0], "message": r[1], "time": str(r[2]), "task": r[3]} for r in rows]}
