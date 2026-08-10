import psycopg2
import os
from dotenv import load_dotenv
from db_connection import get_connection

load_dotenv()

conn = get_connection()
conn.autocommit = True
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name STRING NOT NULL,
    phone STRING,
    email STRING,
    mode STRING DEFAULT 'standard',
    caregiver_email STRING,
    google_id STRING,
    created_at TIMESTAMPTZ DEFAULT now()
)""")
print("Table: users")

cur.execute("""
CREATE TABLE IF NOT EXISTS locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name STRING NOT NULL,
    lat FLOAT NOT NULL,
    lng FLOAT NOT NULL,
    radius_meters INT DEFAULT 150,
    address STRING,
    created_at TIMESTAMPTZ DEFAULT now()
)""")
print("Table: locations")

cur.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    location_id UUID REFERENCES locations(id),
    title STRING NOT NULL,
    description STRING,
    status STRING DEFAULT 'pending',
    priority INT DEFAULT 1,
    photo_s3_key STRING,
    embedding VECTOR(384),
    created_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
)""")
print("Table: tasks")

cur.execute("""
CREATE TABLE IF NOT EXISTS location_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    location_id UUID REFERENCES locations(id),
    event_type STRING NOT NULL,
    lat FLOAT NOT NULL,
    lng FLOAT NOT NULL,
    dwell_minutes INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
)""")
print("Table: location_events")

cur.execute("""
CREATE TABLE IF NOT EXISTS nudge_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    task_id UUID REFERENCES tasks(id),
    trigger_type STRING NOT NULL,
    message STRING,
    delivered BOOL DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
)""")
print("Table: nudge_events")

cur.execute("""
CREATE TABLE IF NOT EXISTS task_completions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id),
    user_id UUID REFERENCES users(id),
    method STRING,
    confidence FLOAT,
    created_at TIMESTAMPTZ DEFAULT now()
)""")
print("Table: task_completions")

cur.execute("""
CREATE TABLE IF NOT EXISTS caregiver_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    caregiver_email STRING NOT NULL,
    notify_on_miss BOOL DEFAULT true,
    notify_on_overtime BOOL DEFAULT true,
    max_store_minutes INT DEFAULT 45,
    created_at TIMESTAMPTZ DEFAULT now()
)""")
print("Table: caregiver_links")

cur.execute("CREATE VECTOR INDEX IF NOT EXISTS tasks_embedding_idx ON tasks (embedding)")
print("Index: vector")

cur.execute("CREATE INDEX IF NOT EXISTS tasks_user_status_idx ON tasks (user_id, status)")
print("Index: tasks_user_status")

cur.execute("CREATE INDEX IF NOT EXISTS location_events_user_time_idx ON location_events (user_id, created_at DESC)")
print("Index: location_events_user_time")

cur.execute("CREATE INDEX IF NOT EXISTS nudge_events_user_task_idx ON nudge_events (user_id, task_id, trigger_type)")
print("Index: nudge_events_user_task")

cur.execute("""
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' ORDER BY table_name
""")
print("\nTables created:")
for row in cur.fetchall():
    print(f"  {row[0]}")

conn.close()
print("\nDatabase setup complete!")
