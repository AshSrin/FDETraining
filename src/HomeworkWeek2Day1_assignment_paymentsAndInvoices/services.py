
from repository import load_invoices, load_payments, find_invoice_by_id, find_payments_by_invoice_id, update_invoice
from model import Invoice, Payment

normalize_invoice = lambda invoice: Invoice(**invoice) if invoice else None
normalize_payment = lambda payment: Payment(**payment) if payment else None
normalize_invoices = lambda invoices: [normalize_invoice(invoice) for invoice in invoices]
normalize_payments = lambda payments: [normalize_payment(payment) for payment in payments]


clean_vendorname = lambda vendor: vendor.strip().title() if vendor else None




creditNote = lambda invoice, payment: {
    "invoice_id": invoice.invoice_id,
    "vendor": invoice.vendor,
    "amount": invoice.amount,
    "status": invoice.status,
    "approval": invoice.approval,
    "paid": payment.paid
}   

def clean_invoice(invoice: Invoice) -> Invoice:
    """Cleans the vendor name in the invoice."""
    invoice.vendor = clean_vendorname(invoice.vendor)
    print(f"Cleaned invoice: {invoice}")
    return invoice  


def build_credit_note(invoice: Invoice, payment: Payment) -> dict:
    """Builds a credit note from the invoice and payment."""
    return creditNote(invoice, payment)

def findDuplicateInvoices(invoices: list[Invoice]) -> list[Invoice]:
    """Finds duplicate invoices based on invoice_id."""
    seen = set()
    duplicates = []
    for invoice in invoices:
        if invoice.invoice_id in seen:
            duplicates.append(invoice)
        else:
            seen.add(invoice.invoice_id)
    print(f"Duplicate invoices: {duplicates}")
    return duplicates

def findDuplicatePayments(payments: list[Payment]) -> list[Payment]:    
    """Finds duplicate payments based on invoice_id."""
    seen = set()
    duplicates = []
    for payment in payments:
        if payment.invoice_id in seen:
            duplicates.append(payment)
        else:
            seen.add(payment.invoice_id)
    print(f"Duplicate payments: {duplicates}")
    return duplicates

def reconcile_invoices_and_payments(invoices: list[Invoice], payments: list[Payment]) -> list[dict]:
    """Reconciles invoices and payments to generate credit notes."""
    credit_notes = []
    payment_dict = {payment.invoice_id: payment for payment in payments}
    
    for invoice in invoices:
        payment = payment_dict.get(invoice.invoice_id)
        if payment:
            credit_note = build_credit_note(invoice, payment)
            credit_notes.append(credit_note)
    print(f"Credit notes: {credit_notes}")
    return credit_notes


invoice = load_invoices() # Load the first invoice for demonstration
cleaned_invoice = clean_invoice(normalize_invoice(invoice))
print(cleaned_invoice.vendor)
   # reconcile_invoices_and_payments(invoices, payments)
   # findDuplicateInvoices(invoices)
   # findDuplicatePayments(payments)
