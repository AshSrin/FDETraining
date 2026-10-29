from database import get_connection

def findinvoice_by_id(invoice_id):
    """Fetches an invoice from the database based on the provided invoice_id."""
    conn = get_connection()
    if conn is None:
        return {"error": "Database connection failed."}
    
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM invoices WHERE invoice_id = %s", (invoice_id,))
            invoice = cur.fetchone()
            print("Fetched invoice:", invoice)  # Debugging statement
            if invoice:
                return {
                    "invoice_id": invoice[0],
                    "vendor": invoice[1],
                    "amount": float(invoice[2]),
                    "status": invoice[3],
                    "approval": invoice[4] if invoice[4] else None
                }
            else:
                return {"error": "Invoice not found."}
    except Exception as e:
        print("Error fetching invoice:", e)
        return {"error": "An error occurred while fetching the invoice."}
    finally:
        conn.close()

def insert_invoice(invoice_id, vendor, amount, status,approval):
    """Inserts a new invoice into the database."""
    conn = get_connection()
    if conn is None:
        return {"error": "Database connection failed."}
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO invoices (invoice_id,vendor, amount, status, approval) VALUES (%s, %s, %s, %s, %s) RETURNING invoice_id",
                (invoice_id, vendor, amount, status, approval)
            )
            new_invoice_id = cur.fetchone()[0]
            conn.commit()
            return {"id": new_invoice_id}
    except Exception as e:
        print("Error inserting invoice:", e)
        return {"error": "An error occurred while inserting the invoice."}
    finally:
        conn.close()
def update_invoice(invoice_id, vendor=None, amount=None, status=None, approval=None):   
    """Updates an existing invoice in the database based on the provided invoice_id."""
    conn = get_connection()
    if conn is None:
        return {"error": "Database connection failed."}
    
    try:
        with conn.cursor() as cur:
            # Build the update query dynamically based on provided parameters
            update_fields = []
            update_values = []
            if vendor is not None:
                update_fields.append("vendor = %s")
                update_values.append(vendor)
            if amount is not None:
                update_fields.append("amount = %s")
                update_values.append(amount)
            if status is not None:
                update_fields.append("status = %s")
                update_values.append(status)
            if approval is not None:
                update_fields.append("approval = %s")
                update_values.append(approval)

            if not update_fields:
                return {"error": "No fields to update."}
            
            update_query = f"UPDATE invoices SET {', '.join(update_fields)} WHERE invoice_id = %s"
            update_values.append(invoice_id)
            
            cur.execute(update_query, tuple(update_values))
            conn.commit()
            
            if cur.rowcount == 0:
                return {"error": "Invoice not found."}
            
            return {"message": "Invoice updated successfully."}
    except Exception as e:
        print("Error updating invoice:", e)
        return {"error": "An error occurred while updating the invoice."}
    finally:
        conn.close()


def delete_invoice(invoice_id):
    """Deletes an invoice from the database based on the provided invoice_id."""
    conn = get_connection()
    if conn is None:
        return {"error": "Database connection failed."}
    
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM invoices WHERE invoice_id = %s", (invoice_id,))
            conn.commit()
            
            if cur.rowcount == 0:
                return {"error": "Invoice not found."}
            
            return {"message": "Invoice deleted successfully."}
    except Exception as e:
        print("Error deleting invoice:", e)
        return {"error": "An error occurred while deleting the invoice."}
    finally:
        conn.close()

