from db_connection import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("""
INSERT INTO users (name, phone, email, mode, caregiver_email)
VALUES (%s, %s, %s, %s, %s) RETURNING id
""", ("Praveen Kumar", "+91-9999999999", "praveen@example.com", "standard", "caregiver@example.com"))
user_id = cur.fetchone()[0]
print(f"User: {user_id}")

locations = [
    ("Home - Adambakkam", 12.9818475, 80.2095872, 50, "Andal Nagar, Adambakkam, Chennai"),
    ("DMart Chennai", 13.0827, 80.2707, 150, "Anna Salai, Chennai"),
    ("Apollo Hospital", 13.0604, 80.2496, 100, "Greams Road, Chennai"),
    ("Office", 12.9953, 80.2460, 100, "Tidel Park, Chennai"),
]

location_ids = {}
for name, lat, lng, radius, address in locations:
    cur.execute("""
    INSERT INTO locations (user_id, name, lat, lng, radius_meters, address)
    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    """, (user_id, name, lat, lng, radius, address))
    loc_id = cur.fetchone()[0]
    location_ids[name] = loc_id
    print(f"Location: {name} → {loc_id}")

tasks = {
    "Home - Adambakkam": [
        ("Pick wallet", "Don't leave without wallet"),
        ("Pick keys", "House keys"),
        ("Turn off gas", "Check gas knob"),
        ("Lock door", "Front door lock"),
    ],
    "DMart Chennai": [
        ("Buy milk", "2 litres full cream"),
        ("Buy vegetables", "Fresh vegetables"),
        ("Buy eggs", "1 dozen eggs"),
    ],
    "Apollo Hospital": [
        ("Take medicines", "Morning medicines"),
        ("Carry insurance card", "Health insurance card"),
    ],
    "Office": [
        ("Lock drawer", "Before leaving"),
        ("Submit timesheet", "Daily timesheet"),
        ("Take laptop charger", "Check bag"),
    ],
}

for loc_name, loc_tasks in tasks.items():
    loc_id = location_ids[loc_name]
    for title, desc in loc_tasks:
        cur.execute("""
        INSERT INTO tasks (user_id, location_id, title, description, status, priority)
        VALUES (%s, %s, %s, %s, 'pending', 1)
        """, (user_id, loc_id, title, desc))
        print(f"  Task: {title}")

conn.commit()

print("\nRow counts:")
for table in ["users", "locations", "tasks"]:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"  {table}: {cur.fetchone()[0]}")

conn.close()
print("\nSeed data complete!")
