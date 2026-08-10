import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("COCKROACHDB_HOST"),
    port=26257,
    user=os.getenv("COCKROACHDB_USER"),
    password=os.getenv("COCKROACHDB_PASSWORD"),
    database="defaultdb",
    sslmode="require",
    sslrootcert="disable"
)
conn.autocommit = True
cur = conn.cursor()
cur.execute("DROP DATABASE IF EXISTS context_memory_pro CASCADE")
print("Dropped: context_memory_pro")
cur.execute("CREATE DATABASE context_memory_pro")
print("Created: context_memory_pro")
conn.close()
print("Done — run setup_database.py next")
