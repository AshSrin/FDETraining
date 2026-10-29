import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / 'data' / 'data.json'

def load_invoices():
    with open(DATA_FILE, 'r') as file:
        data = json.load(file)
    return(data["invoices"])

def load_payments():
    with open(DATA_FILE, 'r') as file:
        data = json.load(file)
        payments = data["payments"]
    return(payments)

def find_invoice_by_id(invoice_id):
    invoices = load_invoices()
    for invoice in invoices:
        if invoice["invoice_id"] == invoice_id:
            return invoice
    return None

def update_invoice(invoice_id, updated_invoice):
    invoices = load_invoices()
    for i, invoice in enumerate(invoices):
        if invoice["invoice_id"] == invoice_id:
            invoices[i] = updated_invoice
            save_invoices(invoices)
            return True
    return False

def add_invoice(new_invoice):
    invoices = load_invoices()
    invoices.append(new_invoice)
    save_invoices(invoices)
    return True

def save_invoices(invoices):
    with open(DATA_FILE, 'r') as file:
        data = json.load(file)
    data["invoices"] = invoices
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def delete_invoice(invoice_id):

    invoices = load_invoices()
    updated_invoices = [invoice for invoice in invoices if invoice["invoice_id"] != invoice_id]
    if len(updated_invoices) == len(invoices):
        return False  # Invoice not found
    save_invoices(updated_invoices)
    return True
