from db_connection import get_connection 
conn = get_connection() 
cur = conn.cursor() 
cur.execute("SELECT title, embedding IS NOT NULL as has_embedding FROM tasks LIMIT 5") 
for row in cur.fetchall(): print(row) 
conn.close() 
