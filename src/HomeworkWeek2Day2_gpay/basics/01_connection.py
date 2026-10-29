import dotenv
import os
import psycopg

dotenv.load_dotenv()  # Load environment variables from .env file

DATABASE_URL = os.getenv("DATABASE_URL")
print("Database URL:", DATABASE_URL)
conn = psycopg.connect(DATABASE_URL)
with conn.cursor() as cur:
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print("Database version:", db_version[0])   