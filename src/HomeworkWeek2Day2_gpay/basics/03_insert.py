import dotenv
import os
import psycopg

dotenv.load_dotenv()  # Load environment variables from .env file

DATABASE_URL = os.getenv("DATABASE_URL")
print("Database URL:", DATABASE_URL)
conn = psycopg.connect(DATABASE_URL)
values=(4, 333, 250.00, 'completed', 'token4')
with conn.cursor() as cur:
        cur.execute("INSERT INTO gpay (id, vendor_id, amount, status, gpay_token) VALUES (%s, %s, %s, %s, %s)", 
                    values)
        conn.commit()