import psycopg
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print('connection string:', DATABASE_URL)



def get_connection():
    """Establishes a connection to the PostgreSQL database using the DATABASE_URL from environment variables."""
    try:
        conn = psycopg.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print("Error connecting to the database:", e)
        return None 
    