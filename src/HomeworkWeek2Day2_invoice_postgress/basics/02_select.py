import psycopg
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print('connection string:', DATABASE_URL)

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM invoices")
        rows = cur.fetchall()
for row in rows:
    print(row)