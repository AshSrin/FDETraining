#generte code with  api router
from fastapi import APIRouter, HTTPException
from models.invoices import Invoices
import services.invoices as invoice_service



router = APIRouter()    

#import the invoice service and use it to get the invoices
@router.get("/invoices")
def get_invoices():
    try:
        invoices = invoice_service.get_invoices()
        return invoices
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: str):
    try:
        invoice = invoice_service.get_invoice(invoice_id)
        return invoice
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
@router.post("/invoices")
def create_invoice(invoice: Invoices):
    try:
        invoice_service.create_invoice(invoice)
        return {"message": "Invoice created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.put("/invoices/{invoice_id}")
def update_invoice(invoice_id: str, invoice: Invoices):
    try:
        invoice_service.update_invoice(invoice_id, invoice)
        return {"message": "Invoice updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: str):
    try:
        invoice_service.delete_invoice(invoice_id)
        return {"message": "Invoice deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/invoices/reconciliation")
def reconcile_invoices():
    try:
        reconciliation_result = invoice_service.run_reconciliation()
        return reconciliation_result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 




