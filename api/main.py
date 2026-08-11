from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from api.routes import location, tasks, nudge, auth, search

app = FastAPI(title="Context Memory Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(location.router, prefix="/location", tags=["location"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(nudge.router, prefix="/nudge", tags=["nudge"])
app.include_router(search.router, prefix="/search", tags=["search"])

@app.get("/health")
def health():
    return {"status": "ok", "version": "pro-1.0", "db": "cockroachdb"}

@app.get("/setup/ids")
def get_test_ids():
    from db_connection import get_connection
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users LIMIT 1")
    user = cur.fetchone()
    cur.execute("SELECT id FROM locations LIMIT 1")
    loc = cur.fetchone()
    conn.close()
    return {
        "user_id": str(user[0]) if user else None,
        "location_id": str(loc[0]) if loc else None
    }

@app.post("/reset")
def reset_demo():
    from db_connection import get_connection
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM nudge_events")
    cur.execute("DELETE FROM location_events")
    cur.execute("DELETE FROM task_completions")
    cur.execute("UPDATE tasks SET status = 'pending', completed_at = NULL")
    conn.commit()
    conn.close()
    return {"status": "reset complete"}

@app.get("/")
def serve_ui():
    return FileResponse("frontend/index.html")

app.mount("/static", StaticFiles(directory="frontend"), name="static")

handler = Mangum(app)