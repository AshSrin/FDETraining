from fastapi import FastAPI,HTTPException
from model import Invoice
from services import create_invoice, get_invoices, delete_invoice, update_invoice

app = FastAPI()
@app.get("/invoices/{invoice_id}", response_model=Invoice)
def get_invoice(invoice_id: str):
    try:
        return get_invoices(invoice_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/invoices", response_model=Invoice)
def create_new_invoice(invoice: Invoice):
    return create_invoice(invoice) 

@app.put("/invoices/{invoice_id}", response_model=Invoice)
def update_existing_invoice(invoice_id: str, updated_invoice: Invoice):
    try:
        return update_invoice(invoice_id, updated_invoice)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
@app.delete("/invoices/{invoice_id}")

def delete_existing_invoice(invoice_id: str):
    try:
        delete_invoice(invoice_id)
        return {"message": f"Invoice with ID {invoice_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    
    