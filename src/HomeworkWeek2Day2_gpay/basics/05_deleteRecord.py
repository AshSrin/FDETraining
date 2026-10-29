import dotenv
import os
import psycopg

dotenv.load_dotenv()  # Load environment variables from .env file

DATABASE_URL = os.getenv("DATABASE_URL")
print("Database URL:", DATABASE_URL)
conn = psycopg.connect(DATABASE_URL)
values=(5, 444, 550.00, 'completed', 'token5')
with conn.cursor() as cur:
        cur.execute("DELETE FROM gpay WHERE id = '4'")
        conn.commit()