from fastapi import APIRouter
from pydantic import BaseModel
from db_connection import get_connection
from typing import Optional

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: str
    google_id: str
    caregiver_email: Optional[str] = ""
    mode: Optional[str] = "standard"

@router.post("/login")
def login_or_create(user: UserCreate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, mode, caregiver_email FROM users WHERE google_id = %s", (user.google_id,))
    existing = cur.fetchone()
    if existing:
        conn.close()
        return {"user": {"id": str(existing[0]), "name": existing[1], "email": existing[2], "mode": existing[3], "caregiver_email": existing[4]}, "created": False}
    cur.execute("""
        INSERT INTO users (name, email, google_id, mode, caregiver_email)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
    """, (user.name, user.email, user.google_id, user.mode, user.caregiver_email))
    user_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return {"user": {"id": str(user_id), "name": user.name, "email": user.email}, "created": True}

@router.get("/user/{google_id}")
def get_user(google_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, mode, caregiver_email FROM users WHERE google_id = %s", (google_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"user": None}
    return {"user": {"id": str(row[0]), "name": row[1], "email": row[2], "mode": row[3], "caregiver_email": row[4]}}
