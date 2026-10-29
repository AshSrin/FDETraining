import psycopg
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print('connection string:', DATABASE_URL)
invoice={
    "invoice_id": 1,
    "vendor": "Vendor A",
    "amount": 100.0,
    "status": "pending",
    "approval": "manager_review"
}

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("INSERT INTO invoices (invoice_id, vendor, amount, status, approval) VALUES (%s, %s, %s, %s, %s)", 
                    (invoice["invoice_id"], invoice["vendor"], invoice["amount"], invoice["status"], invoice["approval"]))
        print("Invoice inserted successfully.")