import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("COCKROACHDB_HOST"),
        port=26257,
        user=os.getenv("COCKROACHDB_USER"),
        password=os.getenv("COCKROACHDB_PASSWORD"),
        database=os.getenv("COCKROACHDB_DATABASE"),
        sslmode="require",
        sslrootcert="disable"
    )
