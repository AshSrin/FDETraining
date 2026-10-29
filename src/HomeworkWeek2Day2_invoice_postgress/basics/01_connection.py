import psycopg
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print('connection string:', DATABASE_URL)

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print("Database version:", db_version[0])   
