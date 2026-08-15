from fastapi import APIRouter
from pydantic import BaseModel
from db_connection import get_connection

router = APIRouter()

class LocationEvent(BaseModel):
    user_id: str
    location_id: str
    event_type: str
    lat: float
    lng: float
    dwell_minutes: int = 0

class LocationCreate(BaseModel):
    user_id: str
    name: str
    lat: float
    lng: float
    radius_meters: int = 150
    address: str = ""

@router.post("/event")
def location_event(event: LocationEvent):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO location_events (user_id, location_id, event_type, lat, lng, dwell_minutes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (event.user_id, event.location_id, event.event_type, event.lat, event.lng, event.dwell_minutes))
    cur.execute("""
        SELECT id, title, description FROM tasks
        WHERE user_id = %s AND location_id = %s AND status = 'pending'
    """, (event.user_id, event.location_id))
    pending = [{"id": str(r[0]), "title": r[1], "description": r[2]} for r in cur.fetchall()]
    conn.commit()
    conn.close()
    return {"event_type": event.event_type, "pending_tasks": pending}

@router.post("/add")
def add_location(loc: LocationCreate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO locations (user_id, name, lat, lng, radius_meters, address)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, name, lat, lng, radius_meters, address
    """, (loc.user_id, loc.name, loc.lat, loc.lng, loc.radius_meters, loc.address))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    return {"location": {"id": str(row[0]), "name": row[1], "lat": row[2], "lng": row[3], "radius_meters": row[4], "address": row[5]}}

@router.get("/list/{user_id}")
def list_locations(user_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, lat, lng, radius_meters, address FROM locations WHERE user_id = %s", (user_id,))
    locations = cur.fetchall()
    result = []
    for loc in locations:
        cur.execute("SELECT status FROM tasks WHERE location_id = %s", (str(loc[0]),))
        tasks = cur.fetchall()
        total = len(tasks)
        pending = len([t for t in tasks if t[0] == "pending"])
        result.append({
            "id": str(loc[0]), "name": loc[1], "lat": loc[2], "lng": loc[3],
            "radius_meters": loc[4], "address": loc[5],
            "total_tasks": total, "pending_tasks": pending
        })
    conn.close()
    return {"locations": result}

class LocationDelete(BaseModel):
    location_id: str
    user_id: str

@router.delete("/delete")
def delete_location(payload: LocationDelete):
    conn = get_connection()
    cur = conn.cursor()
    # Delete tasks first (foreign key)
    cur.execute("DELETE FROM tasks WHERE location_id = %s AND user_id = %s", 
                (payload.location_id, payload.user_id))
    # Delete location events
    cur.execute("DELETE FROM location_events WHERE location_id = %s AND user_id = %s",
                (payload.location_id, payload.user_id))
    # Delete location
    cur.execute("DELETE FROM locations WHERE id = %s AND user_id = %s RETURNING name",
                (payload.location_id, payload.user_id))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    return {"status": "deleted", "location": row[0] if row else None}

class LocationUpdate(BaseModel):
    location_id: str
    user_id: str
    name: str

@router.put("/update")
def update_location(payload: LocationUpdate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE locations SET name = %s WHERE id = %s AND user_id = %s RETURNING name",
                (payload.name, payload.location_id, payload.user_id))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    return {"status": "updated", "name": row[0] if row else None}
