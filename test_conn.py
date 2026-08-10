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
cur = conn.cursor()
cur.execute("SELECT version()")
print(cur.fetchone()[0])
conn.close()
print("Connection successful!")
