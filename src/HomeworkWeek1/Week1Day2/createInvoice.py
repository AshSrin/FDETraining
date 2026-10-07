from fastapi import APIRouter
from invoiceModels import Invoice


create_invoice_router = APIRouter()
@create_invoice_router.post("/createInvoice")
def add_invoice(invoice: Invoice):
    import json

    with open('/Users/srinivasan.ashwini/Documents/fde-week1/src/HomeworkWeek1/invoices.json', 'r+') as file:
        invoices = json.load(file)
        invoices.append(invoice.model_dump())
        file.seek(0)
        json.dump(invoices, file, indent=4)
    return {"message": "Invoice added successfully", "invoice": invoice.model_dump()}